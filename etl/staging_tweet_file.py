from airflow import DAG
from datetime import datetime, timedelta
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

from airflow.providers.amazon.aws.hooks.base_aws import AwsBaseHook
from airflow.operators.python import PythonOperator

from sql.sql_statements import sql_statements
sql = sql_statements()


def insert_from_S3_to_redshift(*args,**kwargs):
    aws_kook = AwsBaseHook('aws_credentials',client_type='redshift')
    credentials = aws_kook.get_credentials()
    redshift_hook = PostgresHook("redshift")
    execution_date = kwargs['execution_date']
    sql_stmt = sql.INSERT_INTO_STAGING_TWEETS_TABLE.format(
        staging_table='staging_tweets',
        s3_bucket='s3://twitter-data-stream/{year}/{month}/{day}/{hour}'.format(
            year=execution_date.year,
            month=str(execution_date.month).zfill(2),
            day=str(execution_date.day).zfill(2),
            hour=str(execution_date.hour).zfill(2)
        ),
        access_key_id=credentials.access_key,
        secret_access_key=credentials.secret_key,
        region='ap-northeast-1',
        json_path='s3://twitter-data-stream-support-files/main_staging_tweets.json'
    )
    redshift_hook.run(sql_stmt)

def insert_into_table(*args,**kwargs):
    redshift_hook = PostgresHook("redshift")
    execution_date = kwargs['execution_date']
    sql_stmt = kwargs['sql'].format(
        year=execution_date.year,
        month=execution_date.month,
        day=execution_date.day,
        hour=execution_date.hour
    )
    redshift_hook.run(sql_stmt)


dag = DAG(
    "tweet_pipeline",
    start_date=datetime(2021, 8, 16, 8, 0, 0, 0),
    schedule_interval='@hourly',
)

create_staging_tweets_table = PostgresOperator(
    task_id="create_staging_tweets_table",
    dag=dag,
    sql=sql.CREATE_STAGING_TWEETS_TABLE,
    postgres_conn_id="redshift"
)

stage_tweets_to_redshift = PythonOperator(
    task_id='stage_tweets',
    dag=dag,
    python_callable=insert_from_S3_to_redshift,
    provide_context=True
)

create_users_table = PostgresOperator(
    task_id="create_users_table",
    dag=dag,
    sql=sql.CREATE_USERS_TABLE,
    postgres_conn_id="redshift"
)

create_hashtags_table = PostgresOperator(
    task_id="create_hashtags_table",
    dag=dag,
    sql=sql.CREATE_HASHTAGS_TABLE,
    postgres_conn_id="redshift"
)

insert_into_users_table = PythonOperator(
    task_id='insert_into_users_table',
    dag=dag,
    python_callable=insert_into_table,
    op_kwargs={'sql':sql.INSERT_INTO_USERS_TABLE},
    provide_context=True
)

insert_into_hasgtags_table = PythonOperator(
    task_id='insert_into_hashtags_table',
    dag=dag,
    python_callable=insert_into_table,
    op_kwargs={'sql':sql.INSERT_INTO_HASHTAGS_TABLE},
    provide_context=True
)


create_staging_tweets_table >> stage_tweets_to_redshift
stage_tweets_to_redshift >> [create_users_table,create_hashtags_table]
create_users_table >> insert_into_users_table
create_hashtags_table >> insert_into_hasgtags_table
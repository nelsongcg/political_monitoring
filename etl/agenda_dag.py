from airflow import DAG
from datetime import datetime, timedelta
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

from airflow.providers.amazon.aws.hooks.base_aws import AwsBaseHook
from airflow.operators.python import PythonOperator

from sql.sql_statements import sql_statements
sql = sql_statements()

def stage_agenda_to_redshift(*args,**kwargs):
    aws_kook = AwsBaseHook('aws_credentials',client_type='redshift')
    credentials = aws_kook.get_credentials()
    redshift_hook = PostgresHook("redshift")
    sql_stmt = sql.INSERT_INTO_STAGING_AGENDA_TABLE.format(
        staging_table='staging_agenda',
        access_key_id=credentials.access_key,
        secret_access_key=credentials.secret_key,
        file='s3://agenda-president/agenda_president.csv'
    )
    redshift_hook.run(sql_stmt)


dag = DAG(
    "agenda_pipeline",
    start_date=datetime(2021, 8, 16, 8, 0, 0, 0),
    schedule_interval='@daily',
)

create_staging_agenda_table = PostgresOperator(
    task_id="create_staging_agenda_table",
    dag=dag,
    sql=sql.CREATE_STAGING_AGENDA_TABLE,
    postgres_conn_id='redshift'
)

stage_agenda_to_redshift = PythonOperator(
    task_id='stage_agenda',
    dag=dag,
    python_callable=stage_agenda_to_redshift,
    provide_context=True
)

create_agenda_president_table = PostgresOperator(
    task_id='create_agenda_president_table',
    dag=dag,
    sql=sql.CREATE_AGENDA_PRESIDENT_TABLE,
    postgres_conn_id='redshift'
)

insert_into_agenda_president_table = PostgresOperator(
    task_id="insert_into_agenda_president_table",
    dag=dag,
    sql=sql.INSERT_INTO_AGENDA_PRESIDENT_TABLE,
    postgres_conn_id="redshift"
)

create_staging_agenda_table >> stage_agenda_to_redshift
stage_agenda_to_redshift >> create_agenda_president_table
create_agenda_president_table >> insert_into_agenda_president_table
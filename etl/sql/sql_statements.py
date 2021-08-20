class sql_statements():

    CREATE_STAGING_TWEETS_TABLE = """
    CREATE TABLE IF NOT EXISTS staging_tweets 
    (
    created_at timestamptz,
    id VARCHAR(255),
    id_str VARCHAR(255),
    text VARCHAR(MAX),
    source VARCHAR(255),
    truncated VARCHAR(255),
    in_reply_to_status_id VARCHAR(255),
    in_reply_to_status_id_str VARCHAR(255),
    in_reply_to_user_id VARCHAR(255),
    in_reply_to_user_id_str VARCHAR(255),
    in_reply_to_screen_name VARCHAR(255),
    user_id VARCHAR(255),
    user_name VARCHAR(255),
    user_screen_name VARCHAR(255),
    user_location VARCHAR(MAX),
    user_url VARCHAR(255),
    user_description VARCHAR(MAX),
    user_protected VARCHAR(255),
    user_verified VARCHAR(255),
    user_followers_count INTEGER,
    user_friends_count INTEGER,
    user_listed_count INTEGER,
    user_favourites_count INTEGER,
    user_statuses_count INTEGER,
    user_created_at timestamptz,
    user_profile_background_color VARCHAR(255),
    user_profile_background_image_url_https VARCHAR(255),
    user_profile_use_background_image VARCHAR(255),
    user_profile_image_url_https VARCHAR(255),
    geo VARCHAR(255),
    coordinates VARCHAR(255),
    place VARCHAR(MAX),
    contributors VARCHAR(255),    
    is_quote_status VARCHAR(255),
    quote_count VARCHAR(255),
    reply_count VARCHAR(255),
    retweet_count VARCHAR(255),
    favorite_count VARCHAR(255),
    entities_hashtags SUPER,
    entities_urls SUPER,
    entities_user_mentions SUPER,
    entities_symbols SUPER,
    favorited VARCHAR(255),
    retweeted VARCHAR(255),
    filter_level VARCHAR(255),
    lang VARCHAR(255),
    timestamp_ms VARCHAR(255)
    )
    """

    INSERT_INTO_STAGING_TWEETS_TABLE = """
    COPY {staging_table} FROM '{s3_bucket}'
    ACCESS_KEY_ID '{access_key_id}' 
    SECRET_ACCESS_KEY '{secret_access_key}' 
    REGION '{region}' 
    JSON '{json_path}'
    timeformat 'auto'
    dateformat 'auto'
    """
    CREATE_USERS_TABLE = """
    CREATE TABLE IF NOT EXISTS users 
    (
    id VARCHAR(255),
    name VARCHAR(255),
    screen_name VARCHAR(255),
    location VARCHAR(MAX),
    url VARCHAR(255),
    description VARCHAR(MAX),
    protected VARCHAR(255),
    verified VARCHAR(255),
    followers_count INTEGER,
    friends_count INTEGER,
    listed_count INTEGER,
    favourites_count INTEGER,
    statuses_count INTEGER,
    created_at timestamptz,
    profile_background_color VARCHAR(255),
    profile_background_image_url_https VARCHAR(255),
    profile_use_background_image VARCHAR(255),
    profile_image_url_https VARCHAR(255)
    )
    """

    CREATE_HASHTAGS_TABLE = """
    CREATE TABLE IF NOT EXISTS hashtags
    (
    created_at timestamptz,
    tweet_id VARCHAR(255),
    user_id VARCHAR(255),
    hashtag VARCHAR(255),
    hashtag_lower VARCHAR(255)
    )
    """

    INSERT_INTO_USERS_TABLE = """
    INSERT INTO users 
    (
      id,
      name,
      screen_name,
      location,
      url,
      description,
      protected,
      verified,
      followers_count,
      friends_count,
      listed_count,
      favourites_count,
      statuses_count,
      created_at,
      profile_background_color,
      profile_background_image_url_https,
      profile_use_background_image,
      profile_image_url_https
    )
    SELECT
        user_id,
        user_name,
        user_screen_name,
        user_location,
        user_url,
        user_description,
        user_protected,
        user_verified,
        user_followers_count,
        user_friends_count,
        user_listed_count,
        user_favourites_count,
        user_statuses_count,
        user_created_at,
        user_profile_background_color,
        user_profile_background_image_url_https,
        user_profile_use_background_image,
        user_profile_image_url_https
    FROM staging_tweets
    WHERE 
    extract(year from created_at) = {year} and
    extract(month from created_at) = {month} and
    extract(day from created_at) = {day} and 
    extract(hour from created_at) = {hour}
    """

    INSERT_INTO_HASHTAGS_TABLE = """
    INSERT INTO hashtags 
    (
      created_at,
      tweet_id,
      user_id,
      hashtag,
      hashtag_lower  
    )
    SELECT 
    st.created_at, 
    st.id, 
    st.user_id, 
    ht.text::varchar as hashtag, 
    LOWER(hashtag) AS hashtag_lower 
    FROM staging_tweets st, st.entities_hashtags AS ht
    WHERE 
    extract(year from created_at) = {year} and
    extract(month from created_at) = {month} and
    extract(day from created_at) = {day} and 
    extract(hour from created_at) = {hour}
    """

SYSTEM_USER = 'SYSTEM'

LOG_FORMAT_CONSOLE = (
    '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | '
    '<level>{level: <8}</level> | '
    'user=<cyan>{extra[username]}</cyan> (id=<cyan>{extra[user_id]}</cyan>) | '
    '<level>{message}</level>'
)

LOG_FORMAT_FILE = (
    '{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | user={extra[username]} (id={extra[user_id]}) | {message}'
)

class User:
    def __init__(self, user_id, telegram_user_id, username, is_manager, manager_id):
        self.user_id = user_id
        self.telegram_user_id = telegram_user_id
        self.username = username
        self.is_manager = is_manager
        self.manager_id = manager_id


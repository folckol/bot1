from aiogram.dispatcher.filters.state import State, StatesGroup

class Start_waiting_group(StatesGroup):

    mailing_choice_1 = State()
    mailing_choice_2 = State()
    waiting_promo = State()

    waiting_admin_message = State()

    main_menu_state = State()

    subgroups_waiting = State()

class Admin_waiting_group(StatesGroup):

    admin_menu_waiting = State()

    # Рассылки
    choose_mailing_variant = State()
    tags_mailing_settings = State()
    id_mailing_settings = State()
    default_mailing_waiting_text = State()
    default_mailing_waiting_next_action = State()
    default_mailing_waiting_link_button_setting = State()
    default_mailing_waiting_message_chain_setting = State()
    default_mailing_waiting_confirm_sending = State()

    # Вопросы
    choose_questions_settings = State()

    new_question = State()
    new_question_wait_number = State()
    new_question_wait_text_description = State()
    new_question_confirm = State()

    edit_question = State()
    waiting_choose_question = State()
    edit_question_edit_name = State()
    edit_question_edit_name_confirm = State()

    edit_number_question = State()
    edit_number_question_confirm = State()

    delete_question = State()
    delete_question_confirm = State()

    # Подразделы
    edit_question_edit_subgroups = State()

    new_subgroup = State()
    new_subgroup_confirm = State()
    delete_subgroup = State()
    delete_subgroup_confirm = State()
    edit_subgroup_title = State()
    edit_subgroup_title_confirm = State()
    edit_subgroup_text = State()
    edit_subgroup_text_confirm = State()

    # Стартовое сообщение
    new_start_message = State()
    new_start_message_confirm = State()

    # Тэги и промокоды
    tags_promos = State()

    tags_settings = State()
    new_tag = State()
    delete_tag = State()

    promos_settings = State()
    new_promo = State()
    new_promo_add_tag = State()
    new_promo_confirm = State()
    delete_promo = State()

    # Переписка с админом
    wait_admin_message = State()
    admin_message_sending_confirm = State()















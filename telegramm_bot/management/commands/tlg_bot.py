from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton
from telegramm_bot.models import (Messages, Patient, Updates,
                                  ProcessedUpdates, Category,
                                  Questions, Session, ProcessedQa,
                                  Answers, Sex)
import time
from datetime import datetime


class Command(BaseCommand):
    help = 'Телеграмм бот'
    text_before_question = 'Ответьте на вопрос:\n'
    gender_selection_msg = "Укажите ваш пол:"
    category_selection_msg = "Выберите категорию:"
    bot = Bot(settings.TOKEN)
    last_update_id = ProcessedUpdates.objects.order_by('id').last()
    upd = ''
    upd_id = ''
    ext_id = ''
    username = ''
    first_name = ''
    last_name = ''
    patient = ''
    chat = ''
    message = ''
    text_from_patient = ''
    clbk_qr_data = ''
    inline_markup = ''
    session = ''
    category = ''

    def parsing_update(self, upd):  # Парсим обновление
        self.upd = upd  # само обновление
        self.upd_id = upd.update_id  # id обновления
        if upd.callback_query:  # если обновление типа callback_query
            self.message = upd.callback_query.message  # объект message
            self.clbk_qr_data = upd.callback_query.data  # data
        else:
            self.message = upd.message
        self.ext_id = self.message.chat.id  # внешнее id пользователя
        self.username = self.message.chat.username  # логин пользователя
        self.first_name = self.message.chat.first_name  # Имя пользователя
        self.last_name = self.message.chat.last_name  # Фамилия пользователя
        self.text_from_patient = self.message.text  # Текст который отправил нам пользователь
        self.chat = self.message.chat  # объет chat

    def create_or_udate_new_patient(self):
  # Получаем из базы данных пользователя, если его нет, создаем.
        self.patient, created = Patient.objects.get_or_create(external_id=self.ext_id,
                                                              defaults={'first_name': self.first_name})
        if self.username:
            self.patient.username = self.username
        else:
            self.patient.username = '-----'
        self.patient.first_name = self.first_name
        if self.last_name:
            self.patient.last_name = self.last_name
        else:
            self.patient.last_name = '-----'
        self.patient.save()

    def save_msg_from_patient(self, upd):
        pass

    def save_updates_id(self, updates):
        """
        Записываем в базу данных id обновлений
        Если обновление с таким id уже было, но прошло более суток,
        удаляем старое, сохраняем новое
        """
        for upd in updates:
            upd_id = upd.update_id
            if upd.callback_query:
                upd_date = upd.callback_query.message.date
            else:
                upd_date = upd.message.date
            update, created = ProcessedUpdates.objects.get_or_create(update_id=upd_id, update_date=upd_date)
            date_now = datetime.now().replace(microsecond=0)
            date_update = update.update_date.replace(microsecond=0, tzinfo=None)
            period = date_now - date_update
            if created:
                update.save()
            elif update.processed and (period.days > 1):
                update.delete()
                update = ProcessedUpdates(update_id=upd_id, update_date=upd_date)
                update.save()

    def save_update(self):
        # Сохраняем обноление, как оно к нам пришло
        this_update = Updates(upd=self.upd)
        this_update.save()

    def save_msg_from_user(self):
        # Сохраняем сообщение от пользователя
        msg = Messages(patient=self.patient, message=self.msg_from_patient)
        msg.save()

    def getInlineKeyboardMarkup(self, button_dict):
        """
        Генерируем объект типа InlineKeyboardMarkup, чтобы в дальнейшем
        вывести в телеграмм в качестве вариантов ответа.
        На вход передается словарь
        """
        column_list = []
        row_list = []
        i = 0
        for key, value in button_dict.items():
            row_list.append(InlineKeyboardButton(key, callback_data=value))
            i += 1
            if i == 2:
                column_list.append(row_list)
                row_list = []
                i = 0
        column_list.append(row_list)
        row_list=[]
        row_list.append(InlineKeyboardButton("Следующий вопрос", callback_data="next"))
        column_list.append(row_list)
        self.inline_markup = InlineKeyboardMarkup(column_list)

    def start_session(self):
        session = Session(patient=self.patient)
        session.save()

    def set_session_finished(self):
        # Устанавливаем сессию законченной
        session = Session.objects.filter(patient=self.patient, finished=False)
        for s in session:
            s.finished = True
            s.save()

    def set_gender(self):
        # Устанавливаем для пользователя, выбранный им пол
        gender = Sex.objects.get(sex_id=self.clbk_qr_data)
        self.patient.sex = gender
        self.patient.save()
        self.message.edit_text(text="Внесенные вами изменения сохранены.")

    def save_processed_qa(self, session, category, question):
        # Сохраняем вопрос-ответ для сессий которые в процессе
        processed_qa = ProcessedQa(session=session, patient=self.patient, category=category,
                                   question=question)
        processed_qa.save()

    def send_question(self):
        # Отправка вопросов пациенту
        answers_list = {}
        exists_session = Session.objects.filter(patient=self.patient, finished=False).exists()
        exists_category = Category.objects.filter(category_id=self.clbk_qr_data).exists()
        if exists_session:
            session = Session.objects.get(patient=self.patient, finished=False)
            if not exists_category:
                # sess = ''
                # for s in session:
                #     sess = s
                processed_qa = ProcessedQa.objects.filter(session=session, patient=self.patient).last()
                processed_qa.patient_answer = Answers.objects.get(answer_id=self.clbk_qr_data)
                processed_qa.save()
                next_q_order = processed_qa.question.q_order + 1
                question = Questions.objects.filter(category=processed_qa.category, q_order=next_q_order).first()
                category = processed_qa.category
                if question:
                    self.save_processed_qa(session, category, question)
                    answers = Answers.objects.filter(question=question)
                    for answer in answers:
                        answers_list[answer.answer] = answer.answer_id
                    self.getInlineKeyboardMarkup(answers_list)
                    self.message.edit_text(text=self.text_before_question + question.question,
                                           reply_markup=self.inline_markup)
                else:
                    self.message.edit_text(text="Ваши ответы обрабатываются")
                    self.set_session_finished()
            else:
                category = Category.objects.get(category_id=self.clbk_qr_data)
                question = Questions.objects.filter(category=category).order_by('q_order').first()
                answers = Answers.objects.filter(question=question)
                for answer in answers:
                    answers_list[answer.answer] = answer.answer_id
                self.getInlineKeyboardMarkup(answers_list)
                self.save_processed_qa(session, category, question)
                self.message.edit_text(text=self.text_before_question + question.question,
                                       reply_markup=self.inline_markup)
        else:
            self.message.edit_text(text="Сессия истекла для данного вопроса")

    def get_list_of_raw_update(self):
        # Создаем список необработанных обновлений
        raw_upd_list = []
        raw_updates = ProcessedUpdates.objects.filter(processed=False)
        for npu in raw_updates:
            raw_upd_list.append(npu.update_id)
        return raw_upd_list

    def callback_query_handling(self):
        # Обработка обновлений типа callback_query_handling
        if self.text_from_patient == self.gender_selection_msg:
            self.set_gender()
        elif self.text_from_patient == self.category_selection_msg:
            self.send_question()
        else:
            self.send_question()

    def msg_start(self):
        # Обработка команды /start
        if self.patient.sex is None:
            self.chat.send_message("Сначала необходимо указать ваш пол, команда /setgender")
        else:
            category = Category.objects.filter(enabled=True)
            but_dict = {}
            for c in category:
                but_dict[c.category] = c.category_id
                self.getInlineKeyboardMarkup(but_dict)
            self.chat.send_message(self.category_selection_msg, reply_markup=self.inline_markup)

    def msg_setgender(self):
        # Обработка команды /setgender
        gender = Sex.objects.all()
        button_dict = {}
        for g in gender:
            if g.id == 1 or g.id == 2:
                button_dict[g.sex] = g.sex_id
        self.getInlineKeyboardMarkup(button_dict)
        self.chat.send_message(self.gender_selection_msg, reply_markup=self.inline_markup)

    def msg_help(self):
        # Обработка команды /help
        self.chat.send_message(self.first_name + ", чтобы начать работу с ботом, вам необходимо \
                               выбрать команду /start, или ввести её вручную")

    def message_handling(self):

        if '/start' in self.text_from_patient:
            self.set_session_finished()
            self.start_session()
            self.msg_start()
        elif '/setgender' in self.text_from_patient:
            self.set_session_finished()
            self.msg_setgender()
        elif '/help' in self.text_from_patient:
            self.set_session_finished()
            self.msg_help()
        else:
            self.set_session_finished()
            self.chat.send_message('Привет' + " " + str(self.first_name))
            self.set_session_finished()

    def handle(self, *args, **options):
        while True:
            update = ""
            try:
                update = self.bot.get_updates(offset=self.last_update_id.update_id)
            except Exception as e:
                pass
            self.save_updates_id(update)
            raw_upd_list = self.get_list_of_raw_update()
            for upd in update:
                self.parsing_update(upd)  # парсим обновление
                if self.upd_id in raw_upd_list:
                    self.save_update()
                    self.create_or_udate_new_patient()
                    if upd.callback_query:
                        self.callback_query_handling()
                    else:
                        self.message_handling()
                    ProcessedUpdates.objects.filter(update_id=self.upd_id).update(processed=True)

        time.sleep(1)

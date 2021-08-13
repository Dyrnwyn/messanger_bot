from django.db import models

# Create your models here.


class Sex(models.Model):
    sex_id = models.CharField(max_length=255, verbose_name="id категории",
                              null=True, editable=False)
    sex = models.CharField(max_length=20, verbose_name="Пол")

    class Meta:
        verbose_name = 'Пол'
        verbose_name_plural = 'Пол'

    def __str__(self):
        return "{0}".format(self.sex)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.sex_id:
            self.sex_id = "sex" + str(self.id)
            self.save()


class Patient(models.Model):
    external_id = models.PositiveIntegerField(unique=True, verbose_name="Внешний ID")
    username = models.CharField(max_length=255, verbose_name="Логин")
    first_name = models.CharField(max_length=255, verbose_name="Имя")
    last_name = models.CharField(max_length=255, verbose_name="Фамилия")
    sex = models.ForeignKey(Sex, on_delete=models.PROTECT,
                            verbose_name="Пол", null=True)

    class Meta:
        verbose_name = "Пациент"
        verbose_name_plural = "Пациенты"

    def __str__(self):
        return "{0}: {1} {2}".format(self.external_id, self.first_name, self.last_name)


class Messages(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT,
                                verbose_name="ID чата")
    message = models.TextField(verbose_name="Сообщение")
    created_at = models.DateTimeField(verbose_name="Время получения",
                                      auto_now_add=True)

    def __str__(self):
        return f'Сообщение {self.pk} от {self.patient}'

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'


class UpdateID(models.Model):
    update_id = models.PositiveIntegerField(verbose_name="ID Обновления",
                                            editable=False)

    class Meta:
        verbose_name = "Последнее ID обновления"
        verbose_name_plural = "ID обновлений"


class Updates(models.Model):
    upd = models.TextField(verbose_name='Обновление')

    class Meta:
        verbose_name = "Обновление"
        verbose_name_plural = "Обновления"


class Category(models.Model):
    category_id = models.CharField(max_length=255, verbose_name="id категории",
                                   null=True, editable=False)
    category = models.CharField(max_length=255, verbose_name='Категория')
    enabled = models.BooleanField(verbose_name='Включить', default=False)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return "{0}".format(self.category)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.category_id:
            self.category_id = "category" + str(self.id)
            self.save()


class Questions(models.Model):
    question_id = models.CharField(max_length=255, verbose_name="id вопроса",
                                   editable=False, null=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT,
                                 verbose_name="Категория")
    question = models.TextField(verbose_name="Вопрос")
    q_order = models.PositiveIntegerField(blank=False, default=1,
                                          verbose_name="Номер в очереди вопросов")
    sex = models.ForeignKey(Sex, on_delete=models.PROTECT,
                            verbose_name="Пол", null=True)

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    def __str__(self):
        return "{0}".format(self.question)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.question_id:
            self.question_id = "question" + str(self.id)
            self.save()


class Answers(models.Model):
    answer_id = models.CharField(max_length=255, verbose_name="id вопроса",
                                 editable=False, null=True)
    question = models.ForeignKey(Questions, on_delete=models.PROTECT,
                                 verbose_name="Вопрос")
    answer = models.TextField(verbose_name="Ответ")

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"

    def __str__(self):
        return "{0}".format(self.answer)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.answer_id:
            self.answer_id = "answer" + str(self.id)
            self.save()


class ProcessedUpdates(models.Model):
    update_id = models.PositiveIntegerField(verbose_name="ID Обновления",
                                            editable=False)
    update_date = models.DateTimeField(verbose_name="Дата поступления обновления", auto_now_add=False,
                                       null=True)
    processed = models.BooleanField(default=False, verbose_name="Обработанно")

    class Meta:
        verbose_name = "Обработанное обновление"
        verbose_name_plural = "Обработанные обновления"


class Session(models.Model):
    active = models.BooleanField(default=True, verbose_name="Активная")
    finished = models.BooleanField(default=False, verbose_name="Завершена")
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, null=True,
                                verbose_name="Пациент")

    class Meta:
        verbose_name = "Сессия"
        verbose_name_plural = "Сессии"

    def __str__(self):
        return "{0}".format(self.id)


class ProcessedQa(models.Model):
    session = models.ForeignKey(Session, on_delete=models.PROTECT,
                                verbose_name="Сессия")
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT,
                                verbose_name="Пациент")
    category = models.ForeignKey(Category, on_delete=models.PROTECT,
                                 verbose_name="Категория")
    question = models.ForeignKey(Questions, on_delete=models.PROTECT,
                                 verbose_name="Вопрос")
    patient_answer = models.ForeignKey(Answers, null=True, on_delete=models.PROTECT,
                                       verbose_name="Ответ")

    class Meta:
        verbose_name = "Вопрос-Ответ"
        verbose_name_plural = "Вопросы-Ответы"

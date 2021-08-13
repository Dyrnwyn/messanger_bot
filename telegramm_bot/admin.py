from django.contrib import admin
from telegramm_bot.models import (UpdateID, Patient, Messages, Updates,
                                  Category, ProcessedUpdates, Questions,
                                  Answers, Session, ProcessedQa, Sex)
# Register your models here.


class SexAdmin(admin.ModelAdmin):
    list_display = ('sex',)


class UpdateIDAdmin(admin.ModelAdmin):
    list_display = ('update_id',)


class PatientAdmin(admin.ModelAdmin):
    list_display = ('external_id', 'username', 'first_name', 'last_name', 'sex')


class MessagesAdmin(admin.ModelAdmin):
    list_display = ('patient', 'message', 'created_at')


class UpdatesAdmin(admin.ModelAdmin):
    list_display = ('upd',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category', 'enabled')


class ProcessedUpdatesAdmin(admin.ModelAdmin):
    list_display = ('update_id', 'update_date', 'processed')


class QuestionsAdmin(admin.ModelAdmin):
    list_display = ('category', 'question', 'q_order')


class AnswersAdmin(admin.ModelAdmin):
    list_display = ('question', 'answer')


class SessionAdmin(admin.ModelAdmin):
    list_display = ('active', 'finished')


class ProcessedQaAdmin(admin.ModelAdmin):
    list_display = ('session', 'patient', 'category', 'question', 'patient_answer')


admin.site.register(UpdateID, UpdateIDAdmin)
admin.site.register(Patient, PatientAdmin)
admin.site.register(Messages, MessagesAdmin)
admin.site.register(Updates, UpdatesAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(ProcessedUpdates, ProcessedUpdatesAdmin)
admin.site.register(Questions, QuestionsAdmin)
admin.site.register(Answers, AnswersAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(ProcessedQa, ProcessedQaAdmin)
admin.site.register(Sex, SexAdmin)

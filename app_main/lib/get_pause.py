from django.utils.datetime_safe import datetime


def get_pause(model_settings) -> bool:
    '''
    функция проверяет можно ли сейчас обменнику работать или он стоит на паузе
    '''
    if not bool(model_settings):
        return True

    if model_settings.pause or model_settings.reload_exchange:
        return True

    now_hour = datetime.now().hour
    job_start = model_settings.job_start
    job_end = model_settings.job_end

    if job_start == job_end or (job_start == 0 and job_end == 24) or (job_start == 24 and job_end == 0):
        return False
    elif job_start < job_end:
        if now_hour < job_start or now_hour > job_end:
            return True
    else:  # job_start > job_end:
        if now_hour < job_start and now_hour >= job_end:
            return True

    return False

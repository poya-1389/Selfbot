import re
from datetime import datetime
import pytz
import jdatetime

def get_tehran_time():
    """دریافت زمان رسمی تهران به صورت jdatetime"""
    tehran_tz = pytz.timezone('Asia/Tehran')
    now = datetime.now(tehran_tz)
    return jdatetime.datetime.fromgregorian(datetime=now)

def format_time_for_bio():
    """فرمت‌سازی زمان برای بیو"""
    now = get_tehran_time()
    return now.strftime("%H:%M")  # فقط ساعت و دقیقه

def format_time_for_name():
    """فرمت‌سازی زمان برای نام"""
    now = get_tehran_time()
    return now.strftime("%H:%M")  # برای نام هم می‌توان ساعت و دقیقه گذاشت

def format_date_for_bio():
    """فرمت‌سازی تاریخ برای بیو"""
    now = get_tehran_time()
    return now.strftime("%Y/%m/%d")  # تاریخ شمسی

def extract_phone(text: str):
    """استخراج شماره تلفن از متن"""
    pattern = r'(\+98|0|0098)?9\d{9}'
    match = re.search(pattern, text)
    return match.group(0) if match else None

def extract_code(text: str):
    """استخراج کد تایید از متن"""
    pattern = r'\b\d{5}\b'
    match = re.search(pattern, text)
    return match.group(0) if match else None

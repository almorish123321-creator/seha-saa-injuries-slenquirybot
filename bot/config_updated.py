# Configuration file for Seha Sick Leave Bot - Updated Version

BOT_TOKEN = '8713124620:AAHnV8ksSuCuQvKHimOb7vC1d0ohq-Lg1p8'
ADMIN_USER_ID = '7853478744'

# API Settings
API_BASE_URL = 'https://80-iayzosfpiazlzday7ujjn-d2b18cd3.manusvm.computer' # يمكن تغييرها حسب عنوان الخادم
API_ENDPOINT = '/api/add_leave.php'
API_FULL_URL = API_BASE_URL + API_ENDPOINT

# Paths - Updated for current working directory
FONTS_DIR = '/home/ubuntu/seha_bot/telegram_bot_deploy/fonts'
IMAGES_DIR = '/home/ubuntu/seha_bot/telegram_bot_deploy'
OUTPUT_DIR = "/home/ubuntu/seha_bot/telegram_bot_deploy/output"

# Font paths
NOTO_SANS_ARABIC_BOLD = f'{FONTS_DIR}/noto_sans_arabic/NotoSansArabic-Bold.ttf'
NOTO_SANS_ARABIC_REGULAR = f'{FONTS_DIR}/noto_sans_arabic/NotoSansArabic-Regular.ttf'
TIMES_NR_MT_BOLD = f'{FONTS_DIR}/times_nr_mt/TimesNRMTPro-Bold.otf'
TIMES_NR_MT_REGULAR = f'{FONTS_DIR}/times_nr_mt/TimesNRMTPro-Regular.otf'

# Image paths
SEHA_LOGO = f'{IMAGES_DIR}/شعارصحةseha.jpg'
GEOMETRIC_SHAPE = f'{IMAGES_DIR}/الشكلالهندسي.jpg'
KINGDOM_TEXT = f'{IMAGES_DIR}/كلمةالمملكةالعربيةالسعوديةKingdomofSaudiArabia.jpg'
HOSPITAL_LOGO = f'{IMAGES_DIR}/شعارالمستشفى.png'
HEALTH_INFO_CENTER_LOGO = f'{IMAGES_DIR}/شعارالمركزالوطنيللمعلوماتالصحية.jpg'

# QR Code settings
QR_URL = 'https://www.seha.sa/#/inquiries/slenquiry'

# PDF settings
PDF_WIDTH = 297  # mm
PDF_HEIGHT = 419  # mm


import os

# قراءة التوكن والآيدي من إعدادات Render فقط
BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_USER_ID = int(os.environ.get('ADMIN_USER_ID', 7853478744))

# API Settings
API_BASE_URL = os.environ.get('API_BASE_URL', 'https://www-seha-sa-inquiries-slenquiry.onrender.com')
API_ENDPOINT = '/api/medical-leaves'
API_FULL_URL = API_BASE_URL + API_ENDPOINT

# Paths
FONTS_DIR = './bot/fonts'
IMAGES_DIR = './bot'
OUTPUT_DIR = './bot/output'

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
QR_URL = 'https://www-seha-sa-inquiries-slenquiry.onrender.com'

# PDF settings
PDF_WIDTH = 297  # mm
PDF_HEIGHT = 419  # mm

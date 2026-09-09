import streamlit as st
import io
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib import colors
import os
import json
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

# MUST be the first Streamlit command
st.set_page_config(
    page_title="Admission Management System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS for professional styling - FIXED
st.markdown("""
    <style>
    /* Main Header */
    .main-header {
        font-size: 2.8rem;
        color: white;
        text-align: center;
        padding: 1.5rem;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        font-weight: 700;
        letter-spacing: 1px;
    }
    .main-header small {
        font-size: 1rem;
        display: block;
        opacity: 0.8;
        margin-top: 5px;
    }
    
    /* Sub Headers */
    .sub-header {
        font-size: 1.3rem;
        color: #1a1a2e !important;
        padding: 0.8rem 1rem;
        border-left: 5px solid #0f3460;
        background: linear-gradient(90deg, #e8f0fe 0%, #ffffff 100%);
        margin: 1.5rem 0 1rem 0;
        border-radius: 0 8px 8px 0;
        font-weight: 600;
        border-bottom: 2px solid #0f3460;
    }
    
    /* Info Box */
    .info-box {
        padding: 1.2rem;
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-radius: 10px;
        border: 2px solid #1976d2;
        margin: 1rem 0;
        font-weight: 500;
        color: #0d47a1;
    }
    .info-box b {
        color: #0d47a1;
    }
    
    /* Stat Cards */
    .stat-card {
        padding: 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: transform 0.3s;
    }
    .stat-card:hover {
        transform: translateY(-5px);
    }
    .stat-card.green {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    .stat-card.orange {
        background: linear-gradient(135deg, #f2994a 0%, #f2c94a 100%);
    }
    .stat-card.blue {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    .stat-card.pink {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    .stat-card .number {
        font-size: 2.8rem;
        font-weight: 700;
        display: block;
    }
    .stat-card .label {
        font-size: 1rem;
        opacity: 0.9;
    }
    
    /* Success Box */
    .success-box {
        padding: 1.2rem;
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-radius: 10px;
        border: 2px solid #28a745;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
        color: white;
        border: none;
        padding: 0.6rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(15, 52, 96, 0.4);
    }
    
    /* Table styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 0 1rem 0;
        color: #6c757d;
        border-top: 1px solid #e0e0e0;
        margin-top: 2rem;
    }
    
    /* Report Card */
    .report-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        margin: 1rem 0;
        border: 1px solid #e0e0e0;
    }
    
    .metric-box {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #dee2e6;
    }
    .metric-box .value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0f3460;
    }
    .metric-box .label {
        font-size: 0.9rem;
        color: #6c757d;
    }
    
    /* Highlight box for Auto ID */
    .highlight-box {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        padding: 1rem 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #f57c00;
        margin: 1rem 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .highlight-box strong {
        color: #e65100;
    }
    
    /* Fee card styling - FIXED */
    .fee-card {
        background: white !important;
        padding: 1.5rem !important;
        border-radius: 15px !important;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1) !important;
        margin: 1rem 0 !important;
        border: 1px solid #e0e0e0 !important;
    }
    .fee-card h4 {
        color: #1a1a2e !important;
        border-bottom: 2px solid #0f3460 !important;
        padding-bottom: 0.5rem !important;
        margin-bottom: 1rem !important;
        font-weight: 700 !important;
    }
    .fee-item {
        display: flex !important;
        justify-content: space-between !important;
        padding: 0.5rem 0 !important;
        border-bottom: 1px solid #f0f0f0 !important;
        margin: 0 !important;
    }
    .fee-item.total {
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        border-bottom: 2px solid #0f3460 !important;
        padding-top: 0.8rem !important;
        margin-top: 0.5rem !important;
    }
    .fee-item span:first-child {
        color: #2c3e50 !important;
    }
    .fee-item span:last-child {
        font-weight: 600 !important;
        color: #0f3460 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================
# DATABASE SETUP
# ============================================

def init_database():
    """Initialize SQLite database with required tables"""
    conn = sqlite3.connect('admission_system.db')
    cursor = conn.cursor()
    
    # Create students table with email column
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            reference_no TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT,
            nationality TEXT,
            university TEXT,
            category TEXT,
            program TEXT,
            duration TEXT,
            description TEXT,
            fee_per_sem REAL,
            scholarship_percent INTEGER,
            fee_after_scholarship REAL,
            registration_fee REAL,
            min_payment REAL,
            bank_name TEXT,
            bank_address TEXT,
            beneficiary TEXT,
            account_number TEXT,
            swift_code TEXT,
            ifsc_code TEXT,
            enrollment_date TEXT,
            status TEXT DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create audit log table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            action TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT,
            user_agent TEXT
        )
    ''')
    
    # Create department stats table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS department_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            department TEXT,
            total_offers INTEGER DEFAULT 0,
            accepted INTEGER DEFAULT 0,
            pending INTEGER DEFAULT 0,
            rejected INTEGER DEFAULT 0,
            year INTEGER,
            month INTEGER,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def add_email_column_if_not_exists():
    """Add email column to students table if it doesn't exist"""
    conn = sqlite3.connect('admission_system.db')
    cursor = conn.cursor()
    
    try:
        # Check if email column exists
        cursor.execute("PRAGMA table_info(students)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'email' not in column_names:
            cursor.execute("ALTER TABLE students ADD COLUMN email TEXT")
            conn.commit()
            print("✅ Email column added successfully!")
            
    except Exception as e:
        print(f"⚠️ Error adding email column: {e}")
    
    conn.close()

def generate_student_id():
    """Generate unique student ID"""
    conn = sqlite3.connect('admission_system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM students")
    count = cursor.fetchone()[0] + 1
    conn.close()
    
    year = datetime.now().strftime("%Y")
    return f"STU-{year}-{str(count).zfill(4)}"

def generate_reference_no():
    """Generate unique reference number"""
    conn = sqlite3.connect('admission_system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM students")
    count = cursor.fetchone()[0] + 1
    conn.close()
    
    year = datetime.now().strftime("%Y")
    return f"REF-{year}-{str(count).zfill(4)}"

def save_student_to_db(student_data):
    """Save student data to database"""
    conn = sqlite3.connect('admission_system.db')
    cursor = conn.cursor()
    
    # Generate IDs if not provided
    if not student_data.get('student_id'):
        student_data['student_id'] = generate_student_id()
    if not student_data.get('reference_no'):
        student_data['reference_no'] = generate_reference_no()
    
    # Insert data
    cursor.execute('''
        INSERT INTO students (
            student_id, reference_no, name, email, nationality, university,
            category, program, duration, description, fee_per_sem,
            scholarship_percent, fee_after_scholarship, registration_fee,
            min_payment, bank_name, bank_address, beneficiary,
            account_number, swift_code, ifsc_code, enrollment_date, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        student_data['student_id'],
        student_data['reference_no'],
        student_data['name'],
        student_data.get('email', ''),
        student_data['nationality'],
        student_data['university'],
        student_data['category'],
        student_data['program'],
        student_data['duration'],
        student_data['description'],
        float(student_data['fee_per_sem']),
        int(student_data['scholarship_percent']),
        float(student_data['fee_after_scholarship']),
        float(student_data['registration_fee']),
        float(student_data['min_payment']),
        student_data['bank_name'],
        student_data['bank_address'],
        student_data['beneficiary'],
        student_data['account_number'],
        student_data['swift_code'],
        student_data['ifsc_code'],
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'Active'
    ))
    
    conn.commit()
    conn.close()
    return student_data['student_id'], student_data['reference_no']

def get_all_students():
    """Retrieve all students from database"""
    conn = sqlite3.connect('admission_system.db')
    df = pd.read_sql_query("SELECT * FROM students ORDER BY created_at DESC", conn)
    conn.close()
    return df

def get_student_count():
    """Get total number of students"""
    conn = sqlite3.connect('admission_system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM students")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_active_students():
    """Get count of active students"""
    conn = sqlite3.connect('admission_system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM students WHERE status = 'Active'")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_department_offers():
    """Get offer count by department/category"""
    conn = sqlite3.connect('admission_system.db')
    df = pd.read_sql_query("""
        SELECT category, program, COUNT(*) as offers,
               SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END) as active,
               SUM(CASE WHEN status = 'Inactive' THEN 1 ELSE 0 END) as inactive
        FROM students 
        GROUP BY category, program
        ORDER BY offers DESC
    """, conn)
    conn.close()
    return df

def get_program_stats():
    """Get detailed statistics by program"""
    conn = sqlite3.connect('admission_system.db')
    df = pd.read_sql_query("""
        SELECT 
            category,
            program,
            COUNT(*) as total_offers,
            SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END) as active_offers,
            SUM(CASE WHEN status = 'Inactive' THEN 1 ELSE 0 END) as inactive_offers,
            AVG(fee_per_sem) as avg_fee,
            AVG(scholarship_percent) as avg_scholarship
        FROM students 
        GROUP BY category, program
        ORDER BY total_offers DESC
    """, conn)
    conn.close()
    return df

def get_monthly_trends():
    """Get monthly enrollment trends"""
    conn = sqlite3.connect('admission_system.db')
    df = pd.read_sql_query("""
        SELECT 
            strftime('%Y-%m', enrollment_date) as month,
            category,
            COUNT(*) as enrollments
        FROM students 
        WHERE enrollment_date IS NOT NULL
        GROUP BY strftime('%Y-%m', enrollment_date), category
        ORDER BY month
    """, conn)
    conn.close()
    return df

def log_audit(student_id, action):
    """Log audit trail"""
    conn = sqlite3.connect('admission_system.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO audit_log (student_id, action)
        VALUES (?, ?)
    ''', (student_id, action))
    conn.commit()
    conn.close()

# ============================================
# EMAIL FUNCTION
# ============================================

def send_offer_email(student_email, student_name, student_id, pdf_data):
    """
    Send offer letter via email to the student
    """
    try:
        # Email configuration (Update these with your credentials)
        SMTP_SERVER = "smtp.gmail.com"  # For Gmail
        SMTP_PORT = 587
        SENDER_EMAIL = "your-email@gmail.com"  # Replace with your email
        SENDER_PASSWORD = "your-app-password"  # Replace with your app password
        
        # Create email
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = student_email
        msg['Subject'] = f"Admission Offer Letter - {student_id}"
        
        # Email body
        body = f"""
        Dear {student_name},
        
        We are pleased to inform you that your admission offer letter has been generated.
        
        Student ID: {student_id}
        
        Please find attached your official Admission Offer Letter.
        
        For any queries, please contact the Admissions Office.
        
        Best regards,
        Department of International Affairs
        University of Excellence
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach PDF
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(pdf_data)
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= Offer_Letter_{student_id}.pdf'
        )
        msg.attach(part)
        
        # Send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True, "Email sent successfully!"
        
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"

# ============================================
# COURSE DATABASE
# ============================================

COURSES_DATABASE = {
    "Undergraduate Programs": {
        "Bachelor of Computer Applications (BCA)": {
            "duration": "3 Years",
            "fee_per_sem": 1800.00,
            "description": "Comprehensive program in computer applications and software development",
            "department": "Computer Science"
        },
        "B.Sc. Data Science": {
            "duration": "3 Years",
            "fee_per_sem": 2000.00,
            "description": "Program focusing on data analytics, machine learning, and AI",
            "department": "Data Science"
        },
        "B.Tech in Computer Science": {
            "duration": "4 Years",
            "fee_per_sem": 2500.00,
            "description": "Engineering program with focus on computer science fundamentals",
            "department": "Computer Science"
        },
        "B.Tech in Artificial Intelligence": {
            "duration": "4 Years",
            "fee_per_sem": 2800.00,
            "description": "Specialized program in AI, deep learning, and neural networks",
            "department": "AI & ML"
        },
        "Bachelor of Business Administration (BBA)": {
            "duration": "3 Years",
            "fee_per_sem": 1500.00,
            "description": "Comprehensive business administration and management program",
            "department": "Business Administration"
        },
        "B.Sc. Biotechnology": {
            "duration": "3 Years",
            "fee_per_sem": 2200.00,
            "description": "Program covering molecular biology, genetics, and bioinformatics",
            "department": "Biotechnology"
        },
        "BA in Economics": {
            "duration": "3 Years",
            "fee_per_sem": 1400.00,
            "description": "Program focusing on economic theory, policy, and analytics",
            "department": "Economics"
        },
        "B.Sc. Psychology": {
            "duration": "3 Years",
            "fee_per_sem": 1600.00,
            "description": "Program covering clinical, cognitive, and behavioral psychology",
            "department": "Psychology"
        },
        "BA in English Literature": {
            "duration": "3 Years",
            "fee_per_sem": 1300.00,
            "description": "Program focusing on English literature, criticism, and creative writing",
            "department": "English"
        },
        "B.Sc. Mathematics": {
            "duration": "3 Years",
            "fee_per_sem": 1550.00,
            "description": "Program covering pure and applied mathematics",
            "department": "Mathematics"
        }
    },
    "Postgraduate Programs": {
        "Master of Business Administration (MBA)": {
            "duration": "2 Years",
            "fee_per_sem": 3500.00,
            "description": "Advanced program in business management and leadership",
            "department": "Business Administration"
        },
        "M.Sc. Data Science": {
            "duration": "2 Years",
            "fee_per_sem": 3200.00,
            "description": "Advanced program in data science and big data analytics",
            "department": "Data Science"
        },
        "M.Tech in Computer Science": {
            "duration": "2 Years",
            "fee_per_sem": 3800.00,
            "description": "Advanced engineering program in computer science",
            "department": "Computer Science"
        },
        "M.Sc. Artificial Intelligence": {
            "duration": "2 Years",
            "fee_per_sem": 4000.00,
            "description": "Specialized masters program in AI and machine learning",
            "department": "AI & ML"
        },
        "M.Sc. Biotechnology": {
            "duration": "2 Years",
            "fee_per_sem": 3500.00,
            "description": "Advanced program in biotechnology and research",
            "department": "Biotechnology"
        },
        "MA in Economics": {
            "duration": "2 Years",
            "fee_per_sem": 3000.00,
            "description": "Advanced program in economic theory and policy",
            "department": "Economics"
        },
        "M.Sc. Psychology": {
            "duration": "2 Years",
            "fee_per_sem": 3200.00,
            "description": "Advanced program in clinical and research psychology",
            "department": "Psychology"
        },
        "M.A. in English": {
            "duration": "2 Years",
            "fee_per_sem": 2800.00,
            "description": "Advanced program in English literature and linguistics",
            "department": "English"
        }
    },
    "Doctoral Programs": {
        "Ph.D. in Computer Science": {
            "duration": "3-5 Years",
            "fee_per_sem": 4500.00,
            "description": "Research program in computer science and related fields",
            "department": "Computer Science"
        },
        "Ph.D. in Data Science": {
            "duration": "3-5 Years",
            "fee_per_sem": 4800.00,
            "description": "Research program in data science and analytics",
            "department": "Data Science"
        },
        "Ph.D. in Business Administration": {
            "duration": "3-5 Years",
            "fee_per_sem": 4200.00,
            "description": "Research program in business administration",
            "department": "Business Administration"
        },
        "Ph.D. in Biotechnology": {
            "duration": "3-5 Years",
            "fee_per_sem": 5000.00,
            "description": "Research program in biotechnology and life sciences",
            "department": "Biotechnology"
        },
        "Ph.D. in Economics": {
            "duration": "3-5 Years",
            "fee_per_sem": 4600.00,
            "description": "Research program in economics and policy",
            "department": "Economics"
        }
    },
    "Diploma & Certificate Programs": {
        "PG Diploma in Data Science": {
            "duration": "1 Year",
            "fee_per_sem": 2500.00,
            "description": "Professional diploma in data science and analytics",
            "department": "Data Science"
        },
        "PG Diploma in AI & ML": {
            "duration": "1 Year",
            "fee_per_sem": 2800.00,
            "description": "Professional diploma in artificial intelligence and machine learning",
            "department": "AI & ML"
        },
        "PG Diploma in Business Analytics": {
            "duration": "1 Year",
            "fee_per_sem": 2300.00,
            "description": "Professional diploma in business analytics",
            "department": "Business Administration"
        },
        "Certificate in Cybersecurity": {
            "duration": "6 Months",
            "fee_per_sem": 2000.00,
            "description": "Certificate program in cybersecurity fundamentals",
            "department": "Computer Science"
        },
        "Certificate in Web Development": {
            "duration": "6 Months",
            "fee_per_sem": 1800.00,
            "description": "Certificate program in full-stack web development",
            "department": "Computer Science"
        },
        "Certificate in Digital Marketing": {
            "duration": "6 Months",
            "fee_per_sem": 1600.00,
            "description": "Certificate program in digital marketing and SEO",
            "department": "Business Administration"
        }
    }
}

def get_course_categories():
    return list(COURSES_DATABASE.keys())

def get_courses_by_category(category):
    if category in COURSES_DATABASE:
        return list(COURSES_DATABASE[category].keys())
    return []

def get_course_details(category, course):
    if category in COURSES_DATABASE and course in COURSES_DATABASE[category]:
        return COURSES_DATABASE[category][course]
    return None

def get_departments():
    """Get unique departments from course database"""
    departments = set()
    for category in COURSES_DATABASE.values():
        for course in category.values():
            if 'department' in course:
                departments.add(course['department'])
    return sorted(list(departments))

# ============================================
# PDF GENERATION
# ============================================

def generate_admission_pdf(student_data):
    """Generates a professional multi-page Admission Offer Letter"""
    buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45,
        title=f"Offer_Letter_{student_data['name'].replace(' ', '_')}"
    )
    
    styles = getSampleStyleSheet()
    
    # Enhanced Typography Styles
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Heading1'], fontName='Helvetica-Bold',
        fontSize=20, leading=24, alignment=TA_CENTER, spaceAfter=10,
        textColor=colors.HexColor('#1a1a2e')
    )
    subtitle_style = ParagraphStyle(
        'SubTitle', parent=styles['Heading2'], fontName='Helvetica',
        fontSize=12, leading=16, alignment=TA_CENTER, spaceAfter=20,
        textColor=colors.HexColor('#6c757d')
    )
    body_style = ParagraphStyle(
        'DocBody', parent=styles['Normal'], fontName='Helvetica',
        fontSize=10, leading=15, textColor=colors.HexColor('#2D3748'), alignment=TA_JUSTIFY
    )
    meta_style = ParagraphStyle(
        'MetaText', parent=styles['Normal'], fontName='Helvetica',
        fontSize=9, leading=12
    )
    table_cell = ParagraphStyle(
        'TableCell', parent=styles['Normal'], fontName='Helvetica',
        fontSize=10, leading=13
    )
    table_cell_bold = ParagraphStyle(
        'TableCellBold', parent=table_cell, fontName='Helvetica-Bold'
    )
    table_header = ParagraphStyle(
        'TableHeader', parent=styles['Normal'], fontName='Helvetica-Bold',
        fontSize=11, leading=14, textColor=colors.white, alignment=TA_CENTER
    )

    story = []
    
    # --- PAGE 1: OFFER & FEES ---
    header_table = [
        [Paragraph("<b>UNIVERSITY OF EXCELLENCE</b>", ParagraphStyle('UniName', parent=meta_style, fontSize=16, textColor=colors.HexColor('#1a1a2e'), alignment=TA_CENTER))]
    ]
    t_header = Table(header_table, colWidths=[522])
    t_header.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_header)
    story.append(Paragraph("Excellence in Education Since 1990", ParagraphStyle('Motto', parent=meta_style, fontSize=9, textColor=colors.HexColor('#6c757d'), alignment=TA_CENTER)))
    story.append(Spacer(1, 10))
    story.append(Paragraph("<hr color='#1a1a2e' size='2'/>", meta_style))
    story.append(Spacer(1, 10))
    
    # Reference Info
    current_date = datetime.now().strftime("%d %b %Y")
    ref_and_date = [
        [Paragraph(f"<b>Reference No.:</b> {student_data['reference_no']}", meta_style), 
         Paragraph(f"<b>Date:</b> {current_date}", ParagraphStyle('R', parent=meta_style, alignment=TA_RIGHT))],
        [Paragraph(f"<b>Student ID No.:</b> {student_data['student_id']}", meta_style), 
         Paragraph(f"<b>Nationality:</b> {student_data['nationality']}", ParagraphStyle('R', parent=meta_style, alignment=TA_RIGHT))]
    ]
    t_meta = Table(ref_and_date, colWidths=[261, 261])
    t_meta.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 20))
    
    # Document Title
    story.append(Paragraph("ADMISSION OFFER LETTER", title_style))
    story.append(Paragraph(f"Academic Year {datetime.now().strftime('%Y')} - {str(int(datetime.now().strftime('%Y')) + 1)}", subtitle_style))
    story.append(Spacer(1, 15))
    
    # Salutation
    story.append(Paragraph(f"Dear <b>{student_data['name']}</b>,", body_style))
    story.append(Spacer(1, 8))
    
    # Opening Text
    opening_text = (
        f"We are pleased to inform you that the Academic Board of <b>{student_data['university']}</b> has reviewed "
        f"your application along with the submitted documents and has found you eligible for admission to the "
        f"academic programs listed below for the academic session {datetime.now().strftime('%Y')}. Accordingly, an Offer Letter is hereby "
        f"issued for your acceptance. Kindly confirm your acceptance by paying the prescribed registration fee "
        f"within 25 days from the date of issue of this letter."
    )
    story.append(Paragraph(opening_text, body_style))
    story.append(Spacer(1, 15))
    
    # Program & Fee Matrix Table
    fee_matrix = [
        [Paragraph("<b>Program Details</b>", table_header), Paragraph("<b>Information</b>", table_header)],
        [Paragraph("Program Category", table_cell), Paragraph(student_data['category'], table_cell_bold)],
        [Paragraph("Program Name", table_cell), Paragraph(student_data['program'], table_cell_bold)],
        [Paragraph("Program Duration", table_cell), Paragraph(student_data['duration'], table_cell)],
        [Paragraph("Program Description", table_cell), Paragraph(student_data['description'], table_cell)],
        [Paragraph("Program Fee (Per Semester)", table_cell), Paragraph(f"<b>USD {student_data['fee_per_sem']}</b>", table_cell_bold)],
        [Paragraph("Scholarship on Program Fee", table_cell), Paragraph(student_data['scholarship_percent'] + "%", table_cell)],
        [Paragraph("Program Fee after Scholarship", table_cell), Paragraph(f"<b>USD {student_data['fee_after_scholarship']}</b>", table_cell_bold)],
        [Paragraph("Registration Fee (One-Time)", table_cell), Paragraph(f"<b>USD {student_data['registration_fee']}</b> (Non-Refundable)", table_cell_bold)],
        [Paragraph("Minimum Payment for Enrollment", table_cell), Paragraph(f"<b>USD {student_data['min_payment']}</b>", table_cell_bold)],
    ]
    t_fee = Table(fee_matrix, colWidths=[261, 261])
    t_fee.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (1,0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0,0), (1,0), colors.white),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('FONTNAME', (0,0), (1,0), 'Helvetica-Bold'),
    ]))
    story.append(t_fee)
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("*Registration fee is a one-time charge, separate from programme and hostel fees.", ParagraphStyle('Note', parent=body_style, fontSize=9, fontName='Helvetica-Oblique', textColor=colors.HexColor('#6c757d'))))
    story.append(Spacer(1, 15))
    
    # Conditions
    story.append(Paragraph("<b>CONDITIONS FOR ACCEPTANCE</b>", table_cell_bold))
    story.append(Spacer(1, 6))
    
    try:
        reg_fee = float(student_data['registration_fee'])
        min_payment = float(student_data['min_payment'])
        program_fee_part = min_payment - reg_fee
    except:
        reg_fee = 0
        min_payment = 0
        program_fee_part = 0
    
    cond1 = f"1. This admission offer is provisional and valid for the current intake. To confirm your admission, you must pay a minimum of USD {student_data['min_payment']} (USD {student_data['registration_fee']} towards registration fee and USD {program_fee_part:.2f} towards the programme fee) within 25 days. If the payment is not made within this period, the offer will be cancelled."
    story.append(Paragraph(cond1, body_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("2. Admission will be confirmed after verification of the following documents:<br/>&nbsp;&nbsp;&nbsp;&nbsp;a. Proof of fee payment<br/>&nbsp;&nbsp;&nbsp;&nbsp;b. Copy of valid passport and passport-size photograph<br/>&nbsp;&nbsp;&nbsp;&nbsp;c. Academic transcripts (translated into English if required)<br/>&nbsp;&nbsp;&nbsp;&nbsp;d. English Proficiency Test Scores (IELTS/TOEFL)<br/>&nbsp;&nbsp;&nbsp;&nbsp;e. Letter of Recommendation (if applicable)", body_style))
    
    story.append(PageBreak())
    
    # --- PAGE 2: BANK DETAILS & INSTRUCTIONS ---
    story.append(Paragraph("<b>FEE PAYMENT &amp; BANK DETAILS</b>", title_style))
    story.append(Spacer(1, 5))
    
    payment_instructions = [
        "• Please ensure the student's name and student ID are mentioned while making the SWIFT transfer.",
        "• All international payments must be made in US Dollars (USD) only.",
        "• The official fee receipt will be issued once the payment is successfully credited.",
        "• Retain the transaction reference number for future correspondence."
    ]
    for inst in payment_instructions:
        story.append(Paragraph(inst, body_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Please use the following Bank Account details to transfer the Fee:", body_style))
    story.append(Spacer(1, 8))
    
    # Bank Details Table
    bank_matrix = [
        [Paragraph("<b>Bank Details</b>", table_header), Paragraph("<b>Information</b>", table_header)],
        [Paragraph("Bank Name", table_cell), Paragraph(student_data['bank_name'], table_cell)],
        [Paragraph("Bank Address", table_cell), Paragraph(student_data['bank_address'], table_cell)],
        [Paragraph("Beneficiary Account Name", table_cell), Paragraph(f"<b>{student_data['beneficiary']}</b>", table_cell_bold)],
        [Paragraph("Account Number", table_cell), Paragraph(f"<b>{student_data['account_number']}</b>", table_cell_bold)],
        [Paragraph("SWIFT Code", table_cell), Paragraph(student_data['swift_code'], table_cell)],
        [Paragraph("IFSC Code", table_cell), Paragraph(student_data['ifsc_code'], table_cell)],
    ]
    t_bank = Table(bank_matrix, colWidths=[200, 322])
    t_bank.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (1,0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0,0), (1,0), colors.white),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_bank)
    story.append(Spacer(1, 15))
    
    # Important Instructions
    story.append(Paragraph("<b>IMPORTANT INSTRUCTIONS</b>", table_cell_bold))
    story.append(Spacer(1, 6))
    instructions = [
        f"1. You have applied for a full-time program at {student_data['university']}.",
        "2. The full first semester fee must be paid before reporting to the campus.",
        "3. International students must ensure valid health insurance coverage throughout their study period.",
        "4. Admission will be granted only after due verification of the original qualifying documents.",
        "5. All communications regarding admission should be directed to the International Affairs Office.",
        "6. Students must comply with all university rules and regulations as outlined in the student handbook.",
        "7. The offer letter must be presented during visa application (if applicable)."
    ]
    for inst in instructions:
        story.append(Paragraph(inst, body_style))
        story.append(Spacer(1, 3))
    
    story.append(Spacer(1, 20))
    story.append(Paragraph("We wish you a successful and enriching academic journey!", body_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Best regards,", body_style))
    story.append(Spacer(1, 5))
    story.append(Paragraph("<b>Department of International Affairs</b>", body_style))
    story.append(Paragraph("University of Excellence", body_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph("<i>Note: This is a computer-generated Offer Letter; it does not require a physical stamp or signature.</i>", ParagraphStyle('Foot', parent=body_style, fontSize=9, textColor=colors.gray)))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# ============================================
# REPORT GENERATION FUNCTIONS
# ============================================

def create_department_offer_chart(df):
    """Create a bar chart showing offers by department"""
    if df.empty:
        return None
    
    # Aggregate by category (department)
    dept_offers = df.groupby('category')['offers'].sum().reset_index()
    dept_offers = dept_offers.sort_values('offers', ascending=True)
    
    fig = go.Figure(data=[
        go.Bar(
            x=dept_offers['offers'],
            y=dept_offers['category'],
            orientation='h',
            marker=dict(
                color=dept_offers['offers'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Number of Offers")
            ),
            text=dept_offers['offers'],
            textposition='outside',
            textfont=dict(size=12, color='black')
        )
    ])
    
    fig.update_layout(
        title="Offers by Department/Category",
        xaxis_title="Number of Offers",
        yaxis_title="Department",
        height=400,
        margin=dict(l=20, r=20, t=50, b=20),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        showlegend=False
    )
    
    return fig

def create_program_offer_chart(df):
    """Create a bar chart showing offers by program"""
    if df.empty:
        return None
    
    # Get top 10 programs
    top_programs = df.nlargest(10, 'offers')[['program', 'offers', 'active']]
    
    fig = go.Figure(data=[
        go.Bar(
            name='Total Offers',
            x=top_programs['program'],
            y=top_programs['offers'],
            marker_color='#0f3460',
            text=top_programs['offers'],
            textposition='outside'
        ),
        go.Bar(
            name='Active Offers',
            x=top_programs['program'],
            y=top_programs['active'],
            marker_color='#27ae60',
            text=top_programs['active'],
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title="Top 10 Programs by Offers",
        xaxis_title="Program",
        yaxis_title="Number of Offers",
        height=450,
        margin=dict(l=20, r=20, t=50, b=20),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        barmode='group',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )
    )
    
    return fig

def create_monthly_trend_chart(df):
    """Create a line chart showing monthly enrollment trends"""
    if df.empty:
        return None
    
    # Pivot for multi-line chart
    pivot_df = df.pivot(index='month', columns='category', values='enrollments').fillna(0)
    
    fig = go.Figure()
    
    for column in pivot_df.columns:
        fig.add_trace(go.Scatter(
            x=pivot_df.index,
            y=pivot_df[column],
            name=column,
            mode='lines+markers',
            line=dict(width=3),
            marker=dict(size=8)
        ))
    
    fig.update_layout(
        title="Monthly Enrollment Trends by Category",
        xaxis_title="Month",
        yaxis_title="Number of Enrollments",
        height=400,
        margin=dict(l=20, r=20, t=50, b=20),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )
    )
    
    return fig

def create_pie_chart(df):
    """Create a pie chart showing distribution by department"""
    if df.empty:
        return None
    
    dept_dist = df.groupby('category')['offers'].sum().reset_index()
    
    fig = go.Figure(data=[
        go.Pie(
            labels=dept_dist['category'],
            values=dept_dist['offers'],
            hole=0.3,
            marker=dict(
                colors=px.colors.qualitative.Set3
            ),
            textinfo='label+percent',
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title="Offer Distribution by Department",
        height=400,
        margin=dict(l=20, r=20, t=50, b=20),
        font=dict(size=12),
        showlegend=True
    )
    
    return fig

def create_donut_chart(df):
    """Create a donut chart showing active vs inactive offers"""
    if df.empty:
        return None
    
    total_offers = df['offers'].sum()
    active_offers = df['active'].sum()
    inactive_offers = df['inactive'].sum()
    
    fig = go.Figure(data=[
        go.Pie(
            labels=['Active Offers', 'Inactive Offers'],
            values=[active_offers, inactive_offers],
            hole=0.4,
            marker=dict(
                colors=['#27ae60', '#e74c3c']
            ),
            textinfo='label+percent',
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title=f"Total: {total_offers} Offers",
        height=350,
        margin=dict(l=20, r=20, t=50, b=20),
        font=dict(size=12),
        showlegend=True
    )
    
    return fig

def create_department_summary_table(df):
    """Create a summary table by department"""
    if df.empty:
        return None
    
    summary = df.groupby('category').agg({
        'offers': 'sum',
        'active': 'sum',
        'inactive': 'sum'
    }).reset_index()
    
    summary['acceptance_rate'] = (summary['active'] / summary['offers'] * 100).round(1)
    summary = summary.sort_values('offers', ascending=False)
    summary.columns = ['Department', 'Total Offers', 'Active', 'Inactive', 'Acceptance Rate (%)']
    
    return summary

# ============================================
# MAIN APPLICATION
# ============================================

def main():
    """Main Streamlit Application - Professional Admission Management System"""
    
    # Initialize database
    init_database()
    
    # Add email column if it doesn't exist
    add_email_column_if_not_exists()
    
    # Sidebar Navigation - FIXED
    with st.sidebar:
        st.markdown("### 🎓 Navigation")
        page = st.radio(
            "",
            ["🏠 Dashboard", "📝 New Admission", "📊 Student Records", "📈 Reports", "📊 Department Reports", "⚙️ Settings"],
            index=0
        )
        
        st.markdown("---")
        st.markdown("### 📊 System Overview")
        total = get_student_count()
        active = get_active_students()
        
        # Fixed: Using st.markdown with proper HTML and inline styles
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 0.8rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #0f3460;">
            <b style="color: #0f3460;">Total Students:</b> <span style="color: #1a1a2e;">{total}</span>
        </div>
        <div style="background: #f8f9fa; padding: 0.8rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #27ae60;">
            <b style="color: #27ae60;">Active Students:</b> <span style="color: #1a1a2e;">{active}</span>
        </div>
        <div style="background: #f8f9fa; padding: 0.8rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #f39c12;">
            <b style="color: #f39c12;">Programs Offered:</b> <span style="color: #1a1a2e;">{len(COURSES_DATABASE)}</span>
        </div>
        <div style="background: #f8f9fa; padding: 0.8rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #8e44ad;">
            <b style="color: #8e44ad;">Departments:</b> <span style="color: #1a1a2e;">{len(get_departments())}</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 💡 Quick Tips")
        st.caption("• New admissions are automatically assigned IDs")
        st.caption("• All data is stored in SQLite database")
        st.caption("• Export reports for analysis")
        st.caption("• Audit log tracks all activities")
        st.caption("• 📧 Offer letters are automatically sent via email when enabled")
    
    # Dashboard Page
    if page == "🏠 Dashboard":
        st.markdown('<div class="main-header">🏛️ Admission Management Dashboard</div>', unsafe_allow_html=True)
        
        # Statistics Cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <span class="number">{get_student_count()}</span>
                <span class="label">Total Students</span>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stat-card green">
                <span class="number">{get_active_students()}</span>
                <span class="label">Active Students</span>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="stat-card orange">
                <span class="number">{len(COURSES_DATABASE)}</span>
                <span class="label">Program Categories</span>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            total_courses = sum(len(courses) for courses in COURSES_DATABASE.values())
            st.markdown(f"""
            <div class="stat-card pink">
                <span class="number">{total_courses}</span>
                <span class="label">Total Programs</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Recent Students
        st.markdown('<div class="sub-header">📋 Recently Enrolled Students</div>', unsafe_allow_html=True)
        
        df = get_all_students()
        if not df.empty:
            display_cols = ['student_id', 'reference_no', 'name', 'program', 'enrollment_date', 'status']
            df_display = df[display_cols].head(10)
            st.dataframe(df_display, use_container_width=True)
        else:
            st.info("No students enrolled yet. Start by creating a new admission!")
        
        # Quick Actions
        st.markdown('<div class="sub-header">⚡ Quick Actions</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📝 New Admission", use_container_width=True):
                st.session_state.page = "📝 New Admission"
                st.experimental_rerun()
        with col2:
            if st.button("📊 View All Records", use_container_width=True):
                st.session_state.page = "📊 Student Records"
                st.experimental_rerun()
        with col3:
            if st.button("📈 View Reports", use_container_width=True):
                st.session_state.page = "📈 Reports"
                st.experimental_rerun()
    
    # New Admission Page
    elif page == "📝 New Admission":
        st.markdown('<div class="main-header">📝 New Student Admission</div>', unsafe_allow_html=True)
        
        # Generate automatic IDs
        auto_student_id = generate_student_id()
        auto_ref_no = generate_reference_no()
        
        # Highlighted Auto ID section
        st.markdown(f"""
        <div class="highlight-box">
            <strong>📌 Automatic ID Generation</strong><br>
            <span style="font-size: 1.1rem;">Student ID: <strong style="color: #0f3460;">{auto_student_id}</strong></span><br>
            <span style="font-size: 1.1rem;">Reference No: <strong style="color: #0f3460;">{auto_ref_no}</strong></span>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown('<div class="sub-header">👤 Student & Academic Information</div>', unsafe_allow_html=True)
            
            name = st.text_input("Student Full Name *", placeholder="Enter full name")
            email = st.text_input("📧 Email Address", placeholder="student@email.com", help="Offer letter will be sent to this email")
            nationality = st.text_input("Nationality *", placeholder="Enter nationality")
            university = st.text_input("University Name *", "University of Excellence")
            
            st.markdown('<div class="sub-header">📚 Program Selection</div>', unsafe_allow_html=True)
            
            col2a, col2b = st.columns(2)
            with col2a:
                category = st.selectbox("Program Category *", get_course_categories())
            
            with col2b:
                courses = get_courses_by_category(category)
                program = st.selectbox("Select Program *", courses)
            
            course_details = get_course_details(category, program)
            if course_details:
                duration = course_details['duration']
                base_fee = course_details['fee_per_sem']
                description = course_details['description']
                st.info(f"📌 {description}")
            else:
                duration = "3 Years"
                base_fee = 1500.00
                description = "Program details not available"
            
            st.markdown('<div class="sub-header">💰 Fee Configuration</div>', unsafe_allow_html=True)
            
            col3a, col3b, col3c = st.columns(3)
            with col3a:
                fee_per_sem = st.number_input("Base Fee Per Semester (USD) *", min_value=0.0, value=float(base_fee), step=100.0, format="%.2f")
            with col3b:
                scholarship_pct = st.slider("Scholarship Grant %", 0, 100, 75)
            with col3c:
                reg_fee = st.number_input("Registration Fee (USD) *", min_value=0.0, value=500.0, step=50.0, format="%.2f")
            
            scholarship_amount = fee_per_sem * (scholarship_pct / 100)
            fee_after_scholarship = fee_per_sem - scholarship_amount
            min_payment = reg_fee + (fee_after_scholarship * 0.5)
            
            st.markdown('<div class="sub-header">🏦 Bank Account Details</div>', unsafe_allow_html=True)
            
            col4a, col4b = st.columns(2)
            with col4a:
                bank_name = st.text_input("Bank Name", "Global Bank International")
                bank_address = st.text_input("Bank Address", "123 Financial District, New York, NY 10001, USA")
                beneficiary = st.text_input("Beneficiary Account Name", "University of Excellence Trust Fund")
            with col4b:
                acc_no = st.text_input("Account Number", "1234567890")
                swift = st.text_input("SWIFT Code", "GBINUS33")
                ifsc = st.text_input("IFSC Code", "GLBKINBB123")
            
            # ============================================
            # EMAIL SETTINGS - VISIBLE OPTION
            # ============================================
            st.markdown('<div class="sub-header">📧 Email Settings</div>', unsafe_allow_html=True)
            
            send_email = st.checkbox("📧 Send Offer Letter via Email", value=True, help="Uncheck if you don't want to send email")
            
            if send_email:
                if email:
                    st.success(f"✅ Offer letter will be sent to: **{email}**")
                else:
                    st.warning("⚠️ Please enter an email address above to send the offer letter")
            else:
                st.info("ℹ️ Email sending is disabled")
            
            st.markdown("---")
            
            if st.button("🎓 Generate & Save Admission", type="primary", use_container_width=True):
                if not name or not nationality or not university:
                    st.error("⚠️ Please fill in all required fields marked with *")
                elif not program:
                    st.error("⚠️ Please select a program")
                else:
                    try:
                        with st.spinner("Processing admission..."):
                            student_data = {
                                'student_id': auto_student_id,
                                'reference_no': auto_ref_no,
                                'name': name,
                                'email': email,
                                'nationality': nationality,
                                'university': university,
                                'category': category,
                                'program': program,
                                'duration': duration,
                                'description': description,
                                'fee_per_sem': f"{fee_per_sem:.2f}",
                                'scholarship_percent': str(scholarship_pct),
                                'fee_after_scholarship': f"{fee_after_scholarship:.2f}",
                                'registration_fee': f"{reg_fee:.2f}",
                                'min_payment': f"{min_payment:.2f}",
                                'bank_name': bank_name,
                                'bank_address': bank_address,
                                'beneficiary': beneficiary,
                                'account_number': acc_no,
                                'swift_code': swift,
                                'ifsc_code': ifsc,
                            }
                            
                            saved_id, saved_ref = save_student_to_db(student_data)
                            log_audit(saved_id, "Admission Generated")
                            pdf_data = generate_admission_pdf(student_data)
                            
                            st.balloons()
                            st.markdown(f"""
                            <div class="success-box">
                                ✅ <b>Admission Generated Successfully!</b><br>
                                Student ID: <b>{saved_id}</b><br>
                                Reference No: <b>{saved_ref}</b>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Download button
                            st.download_button(
                                label="📥 Download Offer Letter PDF",
                                data=pdf_data,
                                file_name=f"Offer_Letter_{name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                            
                            # Send email if checkbox is checked AND email is provided
                            if send_email and email:
                                with st.spinner("📧 Sending email..."):
                                    success, message = send_offer_email(email, name, saved_id, pdf_data)
                                    if success:
                                        st.success(f"📧 Offer letter sent to {email} successfully!")
                                    else:
                                        st.warning(f"⚠️ {message}")
                            elif send_email and not email:
                                st.info("💡 No email address provided. To send email, please add an email address.")
                            else:
                                st.info("💡 Email sending was disabled. Offer letter not sent.")
                            
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        st.exception(e)
        
        with col2:
            # Clean fee summary
            st.markdown('<div class="sub-header">📄 Fee Summary</div>', unsafe_allow_html=True)
            
            st.markdown("""
            <div class="fee-card">
                <h4>Program Details</h4>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class="fee-item">
                    <span>Category</span>
                    <span><b>{category}</b></span>
                </div>
                <div class="fee-item">
                    <span>Program</span>
                    <span><b>{program}</b></span>
                </div>
                <div class="fee-item">
                    <span>Duration</span>
                    <span>{duration}</span>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
                <h4 style="margin-top: 1rem;">Fee Breakdown</h4>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class="fee-item">
                    <span>Base Fee</span>
                    <span>${fee_per_sem:,.2f}</span>
                </div>
                <div class="fee-item">
                    <span>Scholarship</span>
                    <span>{scholarship_pct}%</span>
                </div>
                <div class="fee-item">
                    <span>Scholarship Amount</span>
                    <span style="color: #27ae60;">-${scholarship_amount:,.2f}</span>
                </div>
                <div class="fee-item" style="font-weight: 600; border-bottom: 2px solid #0f3460; padding-bottom: 0.8rem;">
                    <span>Fee after Scholarship</span>
                    <span>${fee_after_scholarship:,.2f}</span>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
                <h4 style="margin-top: 1rem;">Payment Summary</h4>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class="fee-item">
                    <span>Registration Fee</span>
                    <span style="color: #e67e22;">${reg_fee:,.2f}</span>
                </div>
                <div class="fee-item total">
                    <span>Minimum Payment</span>
                    <span style="color: #c0392b;">${min_payment:,.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Additional Note
            st.markdown("""
            <div style="background: #fff3e0; padding: 1rem; border-radius: 8px; margin-top: 1rem; border-left: 4px solid #f57c00;">
                <small style="color: #e65100;">💡 <b>Note:</b> Minimum payment includes registration fee and 50% of first semester fee after scholarship.</small>
            </div>
            """, unsafe_allow_html=True)
    
    # Student Records Page
    elif page == "📊 Student Records":
        st.markdown('<div class="main-header">📊 Student Records</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            search = st.text_input("🔍 Search by Name or ID", placeholder="Enter student name or ID")
        with col2:
            status_filter = st.selectbox("Filter by Status", ["All", "Active", "Inactive", "Graduated"])
        with col3:
            program_filter = st.selectbox("Filter by Program", ["All"] + get_course_categories())
        
        df = get_all_students()
        
        if not df.empty:
            if search:
                df = df[df['name'].str.contains(search, case=False) | df['student_id'].str.contains(search, case=False)]
            if status_filter != "All":
                df = df[df['status'] == status_filter]
            if program_filter != "All":
                df = df[df['category'] == program_filter]
            
            st.markdown(f"**Total Records:** {len(df)}")
            display_cols = ['student_id', 'reference_no', 'name', 'program', 'fee_per_sem', 'enrollment_date', 'status']
            df_display = df[display_cols]
            
            def color_status(val):
                if val == 'Active':
                    return 'background-color: #d4edda'
                elif val == 'Inactive':
                    return 'background-color: #f8d7da'
                elif val == 'Graduated':
                    return 'background-color: #cce5ff'
                return ''
            
            st.dataframe(df_display.style.applymap(color_status, subset=['status']), use_container_width=True)
            
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📥 Export to CSV", use_container_width=True):
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"student_records_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
        else:
            st.info("No student records found in the database.")
    
    # Reports Page
    elif page == "📈 Reports":
        st.markdown('<div class="main-header">📈 Reports & Analytics</div>', unsafe_allow_html=True)
        
        # Get data
        df_offers = get_department_offers()
        df_stats = get_program_stats()
        df_trends = get_monthly_trends()
        
        if not df_offers.empty:
            # Overview Stats
            st.markdown('<div class="sub-header">📊 Overview Statistics</div>', unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="value">{df_offers['offers'].sum()}</div>
                    <div class="label">Total Offers</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="value" style="color: #27ae60;">{df_offers['active'].sum()}</div>
                    <div class="label">Active Offers</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="value" style="color: #e74c3c;">{df_offers['inactive'].sum()}</div>
                    <div class="label">Inactive Offers</div>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                acceptance_rate = (df_offers['active'].sum() / df_offers['offers'].sum() * 100) if df_offers['offers'].sum() > 0 else 0
                st.markdown(f"""
                <div class="metric-box">
                    <div class="value" style="color: #f39c12;">{acceptance_rate:.1f}%</div>
                    <div class="label">Acceptance Rate</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Charts Section
            st.markdown('<div class="sub-header">📊 Visual Analytics</div>', unsafe_allow_html=True)
            
            # Row 1: Two charts side by side
            col1, col2 = st.columns(2)
            
            with col1:
                pie_chart = create_pie_chart(df_offers)
                if pie_chart:
                    st.plotly_chart(pie_chart, use_container_width=True)
            
            with col2:
                donut_chart = create_donut_chart(df_offers)
                if donut_chart:
                    st.plotly_chart(donut_chart, use_container_width=True)
            
            # Row 2: Department bar chart
            dept_chart = create_department_offer_chart(df_offers)
            if dept_chart:
                st.plotly_chart(dept_chart, use_container_width=True)
            
            # Row 3: Program bar chart
            prog_chart = create_program_offer_chart(df_offers)
            if prog_chart:
                st.plotly_chart(prog_chart, use_container_width=True)
            
            # Row 4: Monthly trend
            if not df_trends.empty:
                trend_chart = create_monthly_trend_chart(df_trends)
                if trend_chart:
                    st.plotly_chart(trend_chart, use_container_width=True)
            
            # Department Summary Table
            st.markdown('<div class="sub-header">📋 Department Summary</div>', unsafe_allow_html=True)
            summary_table = create_department_summary_table(df_offers)
            if summary_table is not None:
                st.dataframe(summary_table, use_container_width=True)
                
                # Download report
                csv = summary_table.to_csv(index=False)
                st.download_button(
                    label="📥 Download Summary Report",
                    data=csv,
                    file_name=f"department_summary_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        else:
            st.info("No data available for reports. Start enrolling students!")
    
    # Department Reports Page
    elif page == "📊 Department Reports":
        st.markdown('<div class="main-header">📊 Department-wise Reports</div>', unsafe_allow_html=True)
        
        df_offers = get_department_offers()
        
        if not df_offers.empty:
            # Department selector
            departments = get_departments()
            selected_dept = st.selectbox("Select Department", ["All Departments"] + departments)
            
            if selected_dept != "All Departments":
                # Filter data for selected department
                dept_data = df_offers[df_offers['category'].str.contains(selected_dept, case=False)]
                
                if not dept_data.empty:
                    st.markdown(f'<div class="sub-header">📊 {selected_dept} - Department Report</div>', unsafe_allow_html=True)
                    
                    # Department stats
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Offers", dept_data['offers'].sum())
                    with col2:
                        st.metric("Active Offers", dept_data['active'].sum())
                    with col3:
                        st.metric("Inactive Offers", dept_data['inactive'].sum())
                    with col4:
                        acceptance = (dept_data['active'].sum() / dept_data['offers'].sum() * 100) if dept_data['offers'].sum() > 0 else 0
                        st.metric("Acceptance Rate", f"{acceptance:.1f}%")
                    
                    # Program-wise breakdown
                    st.markdown('<div class="sub-header">📋 Program-wise Breakdown</div>', unsafe_allow_html=True)
                    st.dataframe(dept_data[['program', 'offers', 'active', 'inactive']], use_container_width=True)
                    
                    # Bar chart for programs in department
                    fig = go.Figure(data=[
                        go.Bar(
                            name='Total Offers',
                            x=dept_data['program'],
                            y=dept_data['offers'],
                            marker_color='#0f3460',
                            text=dept_data['offers'],
                            textposition='outside'
                        ),
                        go.Bar(
                            name='Active Offers',
                            x=dept_data['program'],
                            y=dept_data['active'],
                            marker_color='#27ae60',
                            text=dept_data['active'],
                            textposition='outside'
                        )
                    ])
                    
                    fig.update_layout(
                        title=f"Programs in {selected_dept}",
                        xaxis_title="Program",
                        yaxis_title="Number of Offers",
                        height=400,
                        margin=dict(l=20, r=20, t=50, b=20),
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(size=12),
                        barmode='group'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Export department report
                    csv = dept_data.to_csv(index=False)
                    st.download_button(
                        label=f"📥 Download {selected_dept} Report",
                        data=csv,
                        file_name=f"{selected_dept}_report_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    st.warning(f"No data available for {selected_dept}")
            else:
                # Show all departments overview
                st.markdown('<div class="sub-header">📊 All Departments Overview</div>', unsafe_allow_html=True)
                
                # Summary by department
                dept_summary = df_offers.groupby('category').agg({
                    'offers': 'sum',
                    'active': 'sum',
                    'inactive': 'sum'
                }).reset_index()
                
                dept_summary.columns = ['Department', 'Total Offers', 'Active', 'Inactive']
                st.dataframe(dept_summary, use_container_width=True)
                
                # Department bar chart
                fig = go.Figure(data=[
                    go.Bar(
                        x=dept_summary['Department'],
                        y=dept_summary['Total Offers'],
                        marker_color=dept_summary['Total Offers'],
                        marker_colorscale='Viridis',
                        text=dept_summary['Total Offers'],
                        textposition='outside'
                    )
                ])
                
                fig.update_layout(
                    title="Offers by Department",
                    xaxis_title="Department",
                    yaxis_title="Total Offers",
                    height=400,
                    margin=dict(l=20, r=20, t=50, b=20),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Heatmap of departments and programs
                st.markdown('<div class="sub-header">🔥 Department-Program Heatmap</div>', unsafe_allow_html=True)
                
                # Create pivot table for heatmap
                heatmap_data = df_offers.pivot_table(
                    index='category', 
                    columns='program', 
                    values='offers', 
                    fill_value=0
                )
                
                if not heatmap_data.empty:
                    fig = go.Figure(data=go.Heatmap(
                        z=heatmap_data.values,
                        x=heatmap_data.columns,
                        y=heatmap_data.index,
                        colorscale='Viridis',
                        text=heatmap_data.values,
                        texttemplate='%{text}',
                        textfont={"size": 10},
                        hoverongaps=False
                    ))
                    
                    fig.update_layout(
                        title="Offer Distribution Heatmap",
                        height=500,
                        margin=dict(l=20, r=20, t=50, b=20),
                        font=dict(size=10),
                        xaxis=dict(tickangle=45)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for department reports.")
    
    # Settings Page
    elif page == "⚙️ Settings":
        st.markdown('<div class="main-header">⚙️ System Settings</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="sub-header">Database Management</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear All Data", type="secondary", use_container_width=True):
                if st.checkbox("I confirm I want to delete all data"):
                    conn = sqlite3.connect('admission_system.db')
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM students")
                    cursor.execute("DELETE FROM audit_log")
                    cursor.execute("DELETE FROM department_stats")
                    conn.commit()
                    conn.close()
                    st.success("All data cleared successfully!")
        
        with col2:
            if st.button("📦 Backup Database", use_container_width=True):
                if os.path.exists('admission_system.db'):
                    with open('admission_system.db', 'rb') as f:
                        st.download_button(
                            label="Download Backup",
                            data=f,
                            file_name=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db",
                            mime="application/octet-stream"
                        )
        
        st.markdown("---")
        st.markdown('<div class="sub-header">System Information</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"""
            **Database:** SQLite\n
            **Records:** {get_student_count()}\n
            **Departments:** {len(get_departments())}\n
            **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """)
        with col2:
            st.info(f"""
            **Version:** 2.0 Professional\n
            **Platform:** Streamlit\n
            **Status:** 🟢 Operational\n
            **Charts:** Plotly Interactive\n
            **📧 Email:** Automatic offer letters (optional)
            """)
    
    # Footer
    st.markdown("""
    <div class="footer">
        © 2026 University of Excellence - Admission Management System v2.0<br>
        <small>All rights reserved. This system is for authorized use only.</small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
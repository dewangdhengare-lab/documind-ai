"""Script to generate test PDF and DOCX files for DocuMind AI testing."""
import sys
import os

def create_test_docx():
    """Create a test DOCX file with headings and paragraphs."""
    try:
        from docx import Document
        from docx.shared import Pt, Inches
        from docx.enum.text import WD_ALIGN_PARAGRAPH
    except ImportError:
        print("python-docx not installed yet, skipping DOCX creation")
        return False
    
    doc = Document()
    
    # Title
    title = doc.add_heading('Project Phoenix - Implementation Plan', level=0)
    
    doc.add_paragraph('Document Version: 2.1')
    doc.add_paragraph('Last Updated: September 30, 2024')
    doc.add_paragraph('Author: Dr. James Mitchell, Project Director')
    doc.add_paragraph('')
    
    # Section 1
    doc.add_heading('1. Project Overview', level=1)
    doc.add_paragraph(
        'Project Phoenix is a comprehensive digital transformation initiative '
        'designed to modernize the core infrastructure of TechVision Solutions Inc. '
        'The project encompasses the migration of legacy systems to cloud-native '
        'architecture, implementation of AI-driven analytics, and establishment of '
        'a unified data platform. The total project budget is $4.2 million, with '
        'an expected completion date of March 31, 2025.'
    )
    
    # Section 2
    doc.add_heading('2. Objectives', level=1)
    doc.add_paragraph(
        'The primary objectives of Project Phoenix are:'
    )
    objectives = [
        'Migrate 100% of on-premise applications to AWS cloud infrastructure by Q1 2025',
        'Reduce operational costs by 35% through infrastructure optimization',
        'Implement real-time analytics dashboard for business intelligence',
        'Achieve 99.99% uptime SLA for all critical services',
        'Establish automated CI/CD pipelines for all development teams',
        'Complete SOC 2 Type II certification by December 2024',
        'Train 200+ employees on new cloud-native tools and practices',
    ]
    for obj in objectives:
        doc.add_paragraph(obj, style='List Bullet')
    
    # Section 3
    doc.add_heading('3. Timeline and Milestones', level=1)
    
    doc.add_heading('3.1 Phase 1: Foundation (July - September 2024)', level=2)
    doc.add_paragraph(
        'Phase 1 focuses on establishing the cloud infrastructure foundation. '
        'Key deliverables include AWS account setup, network architecture design, '
        'security baseline configuration, and initial team training. Budget allocation: $800,000. '
        'Status: COMPLETED. All Phase 1 milestones were achieved on schedule.'
    )
    
    doc.add_heading('3.2 Phase 2: Migration (October - December 2024)', level=2)
    doc.add_paragraph(
        'Phase 2 involves the systematic migration of existing applications and data. '
        'Priority applications include the Customer Relationship Management (CRM) system, '
        'Enterprise Resource Planning (ERP) platform, and internal communication tools. '
        'Budget allocation: $1.5 million. Status: IN PROGRESS. '
        'The CRM migration is 60% complete. ERP migration begins November 1, 2024.'
    )
    
    doc.add_heading('3.3 Phase 3: Optimization (January - March 2025)', level=2)
    doc.add_paragraph(
        'Phase 3 focuses on performance optimization, cost optimization, and advanced '
        'feature implementation including AI analytics. Budget allocation: $1.9 million. '
        'Status: NOT STARTED. Dependent on successful completion of Phase 2.'
    )
    
    # Section 4
    doc.add_heading('4. Team Structure', level=1)
    doc.add_paragraph(
        'The project team consists of 28 members organized into four workstreams:'
    )
    teams = [
        ('Infrastructure Team', 'Led by Robert Kim, 8 members - Responsible for cloud architecture, networking, and security.'),
        ('Application Team', 'Led by Lisa Wang, 10 members - Responsible for application migration, refactoring, and testing.'),
        ('Data Team', 'Led by Ahmed Hassan, 6 members - Responsible for data migration, analytics, and AI implementation.'),
        ('Change Management', 'Led by Jennifer Park, 4 members - Responsible for training, communication, and adoption.'),
    ]
    for team_name, desc in teams:
        doc.add_paragraph(f'{team_name}: {desc}')
    
    # Section 5
    doc.add_heading('5. Risk Assessment', level=1)
    risks = [
        ('Data Loss During Migration', 'HIGH', 'Comprehensive backup strategy, parallel running of systems during migration, automated data validation checks.'),
        ('Timeline Delays', 'MEDIUM', 'Two-week buffer built into each phase, weekly progress reviews, escalation procedures defined.'),
        ('Budget Overrun', 'MEDIUM', '10% contingency fund ($420,000) reserved, monthly financial reviews, strict change control process.'),
        ('Staff Resistance to Change', 'LOW', 'Early stakeholder engagement, comprehensive training program, dedicated change management team.'),
        ('Security Vulnerabilities', 'HIGH', 'Security-first design approach, automated vulnerability scanning, third-party security audit scheduled for November 2024.'),
    ]
    
    table = doc.add_table(rows=1, cols=3)
    table.style = 'Table Grid'
    header_cells = table.rows[0].cells
    header_cells[0].text = 'Risk'
    header_cells[1].text = 'Severity'
    header_cells[2].text = 'Mitigation Strategy'
    
    for risk, severity, mitigation in risks:
        row_cells = table.add_row().cells
        row_cells[0].text = risk
        row_cells[1].text = severity
        row_cells[2].text = mitigation
    
    # Section 6
    doc.add_heading('6. Budget Summary', level=1)
    doc.add_paragraph(
        'Total Project Budget: $4,200,000\n'
        'Phase 1 (Foundation): $800,000 - SPENT\n'
        'Phase 2 (Migration): $1,500,000 - IN PROGRESS\n'
        'Phase 3 (Optimization): $1,900,000 - NOT STARTED\n'
        'Contingency Reserve: $420,000 (10%)\n'
        'Spent to Date: $920,000\n'
        'Remaining Budget: $3,280,000'
    )
    
    # Section 7
    doc.add_heading('7. Success Criteria', level=1)
    criteria = [
        'All applications migrated to cloud with zero data loss',
        'System uptime maintained at 99.99% or higher',
        'Operational costs reduced by at least 35%',
        'All team members trained and certified on new platform',
        'SOC 2 Type II certification obtained',
        'Customer satisfaction score maintained above 4.5/5.0 during transition',
    ]
    for c in criteria:
        doc.add_paragraph(c, style='List Number')
    
    doc.add_heading('8. Approval', level=1)
    doc.add_paragraph(
        'This implementation plan has been reviewed and approved by:\n\n'
        'Michael Torres, CEO - Approved October 1, 2024\n'
        'Sarah Chen, CFO - Approved October 1, 2024\n'
        'Dr. James Mitchell, Project Director - Approved September 30, 2024\n'
        'Robert Kim, CTO - Approved October 1, 2024'
    )
    
    output_path = os.path.join(os.path.dirname(__file__), 'project_plan.docx')
    doc.save(output_path)
    print(f"Created: {output_path}")
    return True


def create_test_pdf():
    """Create a test PDF file with multiple pages."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib.units import inch
        from reportlab.lib import colors
    except ImportError:
        print("reportlab not installed yet, skipping PDF creation")
        return False
    
    output_path = os.path.join(os.path.dirname(__file__), 'research_paper.pdf')
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Title'], fontSize=18, spaceAfter=20)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading1'], fontSize=14, spaceAfter=12)
    subheading_style = ParagraphStyle('CustomSubHeading', parent=styles['Heading2'], fontSize=12, spaceAfter=10)
    body_style = ParagraphStyle('CustomBody', parent=styles['Normal'], fontSize=10, spaceAfter=8, leading=14)
    
    story = []
    
    # Page 1 - Title and Abstract
    story.append(Paragraph("The Impact of Artificial Intelligence on Modern Healthcare Systems", title_style))
    story.append(Paragraph("A Comprehensive Research Analysis", styles['Heading2']))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Authors: Dr. Emily Richardson, Dr. David Park, Prof. Maria Santos", body_style))
    story.append(Paragraph("Institution: National Institute of Technology Research", body_style))
    story.append(Paragraph("Published: August 2024", body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Abstract", heading_style))
    story.append(Paragraph(
        "This paper examines the transformative impact of artificial intelligence (AI) on modern healthcare "
        "systems across 15 countries over a five-year period (2019-2024). Our research analyzes 2,847 "
        "healthcare facilities that have implemented AI-driven solutions, comparing patient outcomes, "
        "operational efficiency, and cost implications. Key findings indicate that AI implementation in "
        "diagnostic imaging has improved accuracy by 23.4%, while AI-assisted treatment planning has "
        "reduced average hospital stays by 1.8 days. However, significant challenges remain in data "
        "privacy, algorithmic bias, and workforce adaptation. The study concludes with recommendations "
        "for policy makers and healthcare administrators seeking to implement AI solutions effectively "
        "and ethically.", body_style
    ))
    
    story.append(Paragraph("Keywords: artificial intelligence, healthcare, diagnostics, machine learning, patient outcomes, digital health", body_style))
    
    story.append(PageBreak())
    
    # Page 2 - Introduction
    story.append(Paragraph("1. Introduction", heading_style))
    story.append(Paragraph(
        "The integration of artificial intelligence into healthcare represents one of the most significant "
        "technological shifts in modern medicine. Since 2019, global investment in healthcare AI has grown "
        "from $4.9 billion to an estimated $22.4 billion in 2024, reflecting both the promise and the "
        "growing confidence in AI-driven healthcare solutions.", body_style
    ))
    story.append(Paragraph(
        "This research was motivated by the need for comprehensive, cross-national analysis of AI's actual "
        "impact on healthcare delivery. While individual case studies have demonstrated promising results, "
        "there has been limited research examining AI implementation outcomes across diverse healthcare "
        "systems, regulatory environments, and patient populations.", body_style
    ))
    story.append(Paragraph(
        "Our study addresses three fundamental research questions: (1) How does AI implementation affect "
        "diagnostic accuracy and patient outcomes? (2) What are the operational and financial implications "
        "of AI adoption in healthcare facilities? (3) What barriers and challenges do healthcare organizations "
        "face when implementing AI solutions?", body_style
    ))
    
    story.append(Paragraph("1.1 Scope of Study", subheading_style))
    story.append(Paragraph(
        "The study encompasses 2,847 healthcare facilities across 15 countries: United States, United Kingdom, "
        "Germany, France, Japan, South Korea, Canada, Australia, Singapore, India, Brazil, Sweden, Netherlands, "
        "Israel, and China. Facilities range from small community hospitals (under 100 beds) to large academic "
        "medical centers (over 1,000 beds). Data was collected through standardized surveys, electronic health "
        "record analysis, and on-site assessments conducted between January 2023 and June 2024.", body_style
    ))
    
    story.append(PageBreak())
    
    # Page 3 - Methodology
    story.append(Paragraph("2. Methodology", heading_style))
    story.append(Paragraph(
        "Our research employed a mixed-methods approach combining quantitative analysis of clinical outcomes "
        "data with qualitative assessment of implementation experiences.", body_style
    ))
    
    story.append(Paragraph("2.1 Data Collection", subheading_style))
    story.append(Paragraph(
        "Primary data was collected through: (a) structured questionnaires completed by 4,231 healthcare "
        "professionals, (b) analysis of 12.6 million patient records (anonymized), (c) 847 semi-structured "
        "interviews with hospital administrators and IT directors, and (d) financial reports from participating "
        "institutions covering the 2019-2024 period.", body_style
    ))
    
    story.append(Paragraph("2.2 AI Applications Analyzed", subheading_style))
    story.append(Paragraph(
        "The study categorized AI applications into five primary domains:", body_style
    ))
    
    # Table of AI applications
    data = [
        ['Domain', 'Facilities Using', 'Primary Technology'],
        ['Diagnostic Imaging', '1,842 (64.7%)', 'Deep Learning / CNN'],
        ['Clinical Decision Support', '1,456 (51.1%)', 'Natural Language Processing'],
        ['Drug Discovery', '423 (14.9%)', 'Generative AI / ML'],
        ['Administrative Operations', '2,103 (73.9%)', 'RPA / Predictive Analytics'],
        ['Patient Monitoring', '987 (34.7%)', 'IoT / Edge AI'],
    ]
    
    t = Table(data, colWidths=[2*inch, 1.5*inch, 2*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F46E5')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F3F4F6')]),
    ]))
    story.append(t)
    story.append(Spacer(1, 12))
    
    story.append(PageBreak())
    
    # Page 4 - Results
    story.append(Paragraph("3. Key Findings", heading_style))
    
    story.append(Paragraph("3.1 Diagnostic Accuracy", subheading_style))
    story.append(Paragraph(
        "AI-assisted diagnostic imaging demonstrated a statistically significant improvement in accuracy "
        "across all imaging modalities. Radiology AI tools improved detection rates for early-stage cancers "
        "by 23.4% (p < 0.001), with particularly strong performance in breast cancer screening (28.1% "
        "improvement) and lung nodule detection (31.2% improvement). False positive rates decreased by "
        "17.8%, reducing unnecessary biopsies and patient anxiety.", body_style
    ))
    
    story.append(Paragraph("3.2 Patient Outcomes", subheading_style))
    story.append(Paragraph(
        "Facilities with comprehensive AI implementation reported: average hospital stay reduced by 1.8 days "
        "(from 6.3 to 4.5 days), 30-day readmission rates decreased by 12.3%, medication error rates "
        "reduced by 41.7%, and patient satisfaction scores improved by 8.9% on average. The most significant "
        "improvements were observed in facilities that had been using AI for more than 2 years.", body_style
    ))
    
    story.append(Paragraph("3.3 Financial Impact", subheading_style))
    story.append(Paragraph(
        "The average return on AI investment was realized within 2.3 years. Facilities reported average "
        "annual cost savings of $3.2 million for large hospitals (>500 beds) and $890,000 for smaller "
        "facilities. Administrative AI applications showed the fastest ROI (1.4 years), while clinical "
        "AI applications took longer (2.8 years) but delivered greater long-term value. Total investment "
        "in AI across studied facilities averaged $2.1 million for initial implementation and $450,000 "
        "per year for maintenance and updates.", body_style
    ))
    
    story.append(Paragraph("3.4 Challenges Identified", subheading_style))
    story.append(Paragraph(
        "Despite positive outcomes, significant challenges were identified: (1) Data quality issues affected "
        "67% of facilities, requiring extensive data cleaning before AI deployment. (2) Algorithmic bias was "
        "detected in 23% of diagnostic AI tools, particularly in dermatology applications across diverse "
        "skin tones. (3) Staff resistance to AI adoption was reported by 54% of facilities, primarily among "
        "senior physicians. (4) Regulatory compliance complexity was cited as a major barrier by 71% of "
        "facilities, with significant variation across countries.", body_style
    ))
    
    story.append(PageBreak())
    
    # Page 5 - Conclusions
    story.append(Paragraph("4. Conclusions and Recommendations", heading_style))
    story.append(Paragraph(
        "Our comprehensive analysis demonstrates that AI has a measurable, positive impact on healthcare "
        "delivery when implemented thoughtfully. However, success requires careful attention to data quality, "
        "algorithmic fairness, staff training, and regulatory compliance.", body_style
    ))
    
    story.append(Paragraph("4.1 Recommendations for Healthcare Administrators", subheading_style))
    recommendations = [
        "Begin with administrative AI applications (scheduling, billing, documentation) to build organizational familiarity and demonstrate quick wins before moving to clinical applications.",
        "Invest in data infrastructure before AI deployment. Clean, standardized data is the foundation of effective AI systems.",
        "Establish multidisciplinary AI governance committees including clinicians, data scientists, ethicists, and patient representatives.",
        "Prioritize AI solutions that augment clinical decision-making rather than replace human judgment. The most successful implementations were those where AI served as a 'second opinion' tool.",
        "Budget for ongoing maintenance, updates, and staff training. AI systems require continuous monitoring and improvement.",
    ]
    for i, rec in enumerate(recommendations, 1):
        story.append(Paragraph(f"{i}. {rec}", body_style))
    
    story.append(Paragraph("4.2 Recommendations for Policy Makers", subheading_style))
    story.append(Paragraph(
        "Governments should establish clear regulatory frameworks for healthcare AI that balance innovation "
        "with patient safety. International harmonization of AI regulations would facilitate cross-border "
        "collaboration and reduce compliance costs. Public funding for AI bias research and mitigation "
        "strategies is essential to ensure equitable healthcare delivery.", body_style
    ))
    
    story.append(Paragraph("References", heading_style))
    refs = [
        "World Health Organization. (2023). Ethics and Governance of Artificial Intelligence for Health. WHO Press.",
        "Smith, J. et al. (2023). 'AI in Radiology: A Five-Year Retrospective Analysis.' Nature Medicine, 29(4), 112-128.",
        "Johnson, L. & Park, D. (2024). 'Financial Impact of Healthcare AI: A Multi-Center Study.' Health Economics Review, 14(1), 45-67.",
        "European Commission. (2024). AI Act: Regulatory Framework for Artificial Intelligence. Brussels.",
        "Chen, W. et al. (2023). 'Addressing Algorithmic Bias in Healthcare AI Systems.' The Lancet Digital Health, 5(8), 445-456.",
    ]
    for ref in refs:
        story.append(Paragraph(ref, body_style))
    
    doc.build(story)
    print(f"Created: {output_path}")
    return True


def create_second_report():
    """Create a second TXT document that overlaps with the first for comparison testing."""
    content = """Annual Strategic Review 2024 - TechVision Solutions Inc.

Prepared by: Michael Torres, Chief Executive Officer
Date: November 1, 2024

1. Company Overview

TechVision Solutions Inc. has completed another transformative year. As we approach the end of 2024, the company has demonstrated strong growth across all divisions, with total annual revenue projected to reach $47 million, exceeding our initial target of $44 million by 6.8%.

The workforce has grown to 356 employees, up from 298 at the start of the year. Our client base has expanded to 312 active accounts, with a retention rate of 94.2%.

2. Financial Performance

Annual revenue progression:
- 2022: $32.4 million
- 2023: $38.7 million
- 2024 (projected): $47.0 million

Revenue breakdown by division:
- Cloud Services: $26.8 million (57% of total) - Growth: 28%
- Consulting: $14.1 million (30% of total) - Growth: 12%
- Product Licensing: $6.1 million (13% of total) - Growth: -5%

Operating margin improved from 18.2% in 2023 to 21.5% in 2024, driven by economies of scale in cloud services and automation of internal processes.

3. Strategic Achievements

3.1 Cloud Platform 3.0
The launch of CloudPlatform 3.0 was the defining achievement of 2024. The platform now serves 156 enterprise clients, up from 89 at the end of 2023. Customer satisfaction scores for the platform average 4.6 out of 5.0.

3.2 Project Phoenix
Project Phoenix, our internal digital transformation initiative, has progressed through Phases 1 and 2 successfully. Phase 1 (Foundation) was completed on schedule and within budget. Phase 2 (Migration) is 85% complete as of October 2024. The total project budget of $4.2 million remains on track, with $2.1 million spent to date.

3.3 Security Certification
We achieved SOC 2 Type II certification in November 2024, ahead of the December target. This certification has already contributed to winning three new enterprise contracts valued at $2.3 million combined.

4. Challenges and Lessons Learned

4.1 Talent Market
The technology talent market remained highly competitive throughout 2024. We increased our average compensation by 8% and introduced flexible work arrangements, which improved our offer acceptance rate from 62% to 78%.

4.2 Product Licensing Transition
The transition from perpetual to subscription licensing continued to impact short-term revenue in the product division. However, annual recurring revenue (ARR) for subscription products grew 145% year-over-year, and we project the crossover point in Q2 2025.

4.3 Client Concentration
Despite efforts to diversify, our top 5 clients still represent 31% of total revenue, down from 34% in Q3. This remains an area of focus for 2025.

5. 2025 Strategic Priorities

5.1 AI Analytics Suite
Launch and scale the AI Analytics Suite, targeting $8 million in revenue for 2025. The beta launched in Q4 2024 with 12 pilot clients providing positive feedback.

5.2 Healthcare Vertical
Expand into the healthcare technology market, leveraging our cloud and security capabilities. Target: 20 healthcare clients by end of 2025.

5.3 International Expansion
Open a European office (London) by Q2 2025 to serve growing demand from UK and EU clients. Initial investment: $1.5 million.

5.4 Revenue Target
2025 revenue target: $58 million (23% growth)

5.5 Workforce Planning
Planned headcount growth to 425 employees by end of 2025, with emphasis on AI/ML engineers, healthcare domain specialists, and European sales team.

6. Conclusion

2024 has been a year of strong execution and strategic positioning. TechVision Solutions is well-positioned for continued growth in 2025, with a solid cloud platform, expanding client base, and clear strategic direction. The investments we have made in infrastructure, talent, and security will continue to pay dividends in the coming years.

Michael Torres
Chief Executive Officer
TechVision Solutions Inc.
"""
    output_path = os.path.join(os.path.dirname(__file__), 'annual_review.txt')
    with open(output_path, 'w') as f:
        f.write(content)
    print(f"Created: {output_path}")


if __name__ == '__main__':
    create_second_report()
    create_test_docx()
    create_test_pdf()
    print("\nTest files created successfully!")

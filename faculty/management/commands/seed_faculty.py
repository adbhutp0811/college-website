from django.core.management.base import BaseCommand
from faculty.models import Faculty
from students.models import Class


FACULTY_SEED = [
    # CSE (Computer Science & Engineering)
    {'emp': 'CSE001', 'first': 'I.P.', 'last': 'Mishra', 'desig': 'professor_hod', 'qual': 'Ph.D. (IIT BHU)', 'spec': 'Artificial Intelligence, Machine Learning', 'email': 'ip.mishra@mit.edu', 'phone': '+919810011001', 'exp': '16 years', 'classes': ['CSE-Sem 1', 'CSE-Sem 2', 'CSE-Sem 3']},
    {'emp': 'CSE002', 'first': 'Rohan', 'last': 'Gupta', 'desig': 'associate_professor', 'qual': 'Ph.D. (NIT Trichy)', 'spec': 'Cybersecurity, Cryptography', 'email': 'rohan.gupta@mit.edu', 'phone': '+919810011002', 'exp': '10 years', 'classes': ['CSE-Sem 4', 'CSE-Sem 5']},
    {'emp': 'CSE003', 'first': 'Abhishek', 'last': 'Pandey', 'desig': 'assistant_professor', 'qual': 'M.Tech (IIT Guwahati)', 'spec': 'Cloud Computing, Distributed Systems', 'email': 'abhishek.pandey@mit.edu', 'phone': '+919810011003', 'exp': '5 years', 'classes': ['CSE-Sem 6', 'CSE-Sem 7']},
    {'emp': 'CSE004', 'first': 'Priya', 'last': 'Singh', 'desig': 'assistant_professor', 'qual': 'M.Tech (IIT Delhi)', 'spec': 'Data Science, Big Data Analytics', 'email': 'priya.singh@mit.edu', 'phone': '+919810011004', 'exp': '6 years', 'classes': ['CSE-Sem 5', 'CSE-Sem 8']},
    {'emp': 'CSE005', 'first': 'Amit', 'last': 'Verma', 'desig': 'assistant_professor', 'qual': 'M.Tech (NIT Warangal)', 'spec': 'Web Technologies, Software Engineering', 'email': 'amit.verma@mit.edu', 'phone': '+919810011005', 'exp': '4 years', 'classes': ['CSE-Sem 2', 'CSE-Sem 3', 'CSE-Sem 4']},

    # ECE (Electronics & Communication Eng.)
    {'emp': 'ECE001', 'first': 'Suresh', 'last': 'Kumar', 'desig': 'professor_hod', 'qual': 'Ph.D. (IIT Kanpur)', 'spec': 'VLSI Design, Embedded Systems', 'email': 'suresh.kumar@mit.edu', 'phone': '+919810012001', 'exp': '18 years', 'classes': ['ECE-Sem 1', 'ECE-Sem 2', 'ECE-Sem 3']},
    {'emp': 'ECE002', 'first': 'Neelam', 'last': 'Sharma', 'desig': 'associate_professor', 'qual': 'Ph.D. (IIT Roorkee)', 'spec': 'Signal Processing, Communication Systems', 'email': 'neelam.sharma@mit.edu', 'phone': '+919810012002', 'exp': '12 years', 'classes': ['ECE-Sem 4', 'ECE-Sem 5']},
    {'emp': 'ECE003', 'first': 'Vikas', 'last': 'Yadav', 'desig': 'assistant_professor', 'qual': 'M.Tech (NIT Delhi)', 'spec': 'IoT, Wireless Sensor Networks', 'email': 'vikas.yadav@mit.edu', 'phone': '+919810012003', 'exp': '7 years', 'classes': ['ECE-Sem 5', 'ECE-Sem 6']},
    {'emp': 'ECE004', 'first': 'Anita', 'last': 'Desai', 'desig': 'assistant_professor', 'qual': 'M.Tech (NIT Surat)', 'spec': 'RF Engineering, Microwave', 'email': 'anita.desai@mit.edu', 'phone': '+919810012004', 'exp': '5 years', 'classes': ['ECE-Sem 7', 'ECE-Sem 8']},
    {'emp': 'ECE005', 'first': 'Rahul', 'last': 'Joshi', 'desig': 'assistant_professor', 'qual': 'M.Tech (IIT Bombay)', 'spec': 'Digital Electronics, FPGA Design', 'email': 'rahul.joshi@mit.edu', 'phone': '+919810012005', 'exp': '6 years', 'classes': ['ECE-Sem 3', 'ECE-Sem 4', 'ECE-Sem 6']},

    # ME (Mechanical Engineering)
    {'emp': 'ME001', 'first': 'Dinesh', 'last': 'Patel', 'desig': 'professor_hod', 'qual': 'Ph.D. (IIT Delhi)', 'spec': 'Thermal Engineering, Heat Transfer', 'email': 'dinesh.patel@mit.edu', 'phone': '+919810013001', 'exp': '20 years', 'classes': ['ME-Sem 1', 'ME-Sem 2', 'ME-Sem 3']},
    {'emp': 'ME002', 'first': 'Sunita', 'last': 'Rathore', 'desig': 'associate_professor', 'qual': 'Ph.D. (IIT Madras)', 'spec': 'Manufacturing, Production Engineering', 'email': 'sunita.rathore@mit.edu', 'phone': '+919810013002', 'exp': '13 years', 'classes': ['ME-Sem 4', 'ME-Sem 5']},
    {'emp': 'ME003', 'first': 'Rajeev', 'last': 'Shukla', 'desig': 'assistant_professor', 'qual': 'M.Tech (IIT Kharagpur)', 'spec': 'Automotive Engineering, CAD/CAM', 'email': 'rajeev.shukla@mit.edu', 'phone': '+919810013003', 'exp': '8 years', 'classes': ['ME-Sem 5', 'ME-Sem 6']},
    {'emp': 'ME004', 'first': 'Pooja', 'last': 'Mehta', 'desig': 'assistant_professor', 'qual': 'M.Tech (NIT Calicut)', 'spec': 'Fluid Mechanics, Hydraulics', 'email': 'pooja.mehta@mit.edu', 'phone': '+919810013004', 'exp': '5 years', 'classes': ['ME-Sem 7', 'ME-Sem 8']},
    {'emp': 'ME005', 'first': 'Arun', 'last': 'Singh', 'desig': 'assistant_professor', 'qual': 'M.Tech (IIT Roorkee)', 'spec': 'Strength of Materials, Machine Design', 'email': 'arun.singh@mit.edu', 'phone': '+919810013005', 'exp': '6 years', 'classes': ['ME-Sem 3', 'ME-Sem 4', 'ME-Sem 6']},

    # TT (Textile Technology)
    {'emp': 'TT001', 'first': 'Alok', 'last': 'Kumar', 'desig': 'professor_hod', 'qual': 'Ph.D. (IIT Delhi)', 'spec': 'Fiber Science, Yarn Manufacturing', 'email': 'alok.kumar@mit.edu', 'phone': '+919810014001', 'exp': '15 years', 'classes': ['TT-Sem 1', 'TT-Sem 2', 'TT-Sem 3']},
    {'emp': 'TT002', 'first': 'Sunita', 'last': 'Verma', 'desig': 'associate_professor', 'qual': 'Ph.D. (IIT Kanpur)', 'spec': 'Yarn Manufacturing, Textile Testing', 'email': 'sunita.verma@mit.edu', 'phone': '+919810014002', 'exp': '12 years', 'classes': ['TT-Sem 4', 'TT-Sem 5']},
    {'emp': 'TT003', 'first': 'Rajesh', 'last': 'Singh', 'desig': 'assistant_professor', 'qual': 'M.Tech (NIT Patna)', 'spec': 'Fabric Design, Weaving', 'email': 'rajesh.singh@mit.edu', 'phone': '+919810014003', 'exp': '8 years', 'classes': ['TT-Sem 5', 'TT-Sem 6']},
    {'emp': 'TT004', 'first': 'Neha', 'last': 'Gupta', 'desig': 'assistant_professor', 'qual': 'M.Tech (NIT Jalandhar)', 'spec': 'Textile Testing, Quality Control', 'email': 'neha.gupta@mit.edu', 'phone': '+919810014004', 'exp': '6 years', 'classes': ['TT-Sem 7', 'TT-Sem 8']},
    {'emp': 'TT005', 'first': 'Sanjay', 'last': 'Mishra', 'desig': 'assistant_professor', 'qual': 'M.Tech (IIT BHU)', 'spec': 'Nonwovens, Technical Textiles', 'email': 'sanjay.mishra@mit.edu', 'phone': '+919810014005', 'exp': '5 years', 'classes': ['TT-Sem 3', 'TT-Sem 4', 'TT-Sem 6']},

    # TC (Textile Chemistry)
    {'emp': 'TC001', 'first': 'Priya', 'last': 'Sharma', 'desig': 'professor_hod', 'qual': 'Ph.D. (IIT Bombay)', 'spec': 'Dyeing Chemistry, Color Science', 'email': 'priya.sharma@mit.edu', 'phone': '+919810015001', 'exp': '14 years', 'classes': ['TC-Sem 1', 'TC-Sem 2', 'TC-Sem 3']},
    {'emp': 'TC002', 'first': 'Manoj', 'last': 'Tiwari', 'desig': 'associate_professor', 'qual': 'Ph.D. (IIT Roorkee)', 'spec': 'Polymer Chemistry, Fiber Modification', 'email': 'manoj.tiwari@mit.edu', 'phone': '+919810015002', 'exp': '11 years', 'classes': ['TC-Sem 4', 'TC-Sem 5']},
    {'emp': 'TC003', 'first': 'Anjali', 'last': 'Mishra', 'desig': 'assistant_professor', 'qual': 'M.Tech (MNNIT Allahabad)', 'spec': 'Textile Finishing, Chemical Processing', 'email': 'anjali.mishra@mit.edu', 'phone': '+919810015003', 'exp': '7 years', 'classes': ['TC-Sem 5', 'TC-Sem 6']},
    {'emp': 'TC004', 'first': 'Vivek', 'last': 'Saxena', 'desig': 'assistant_professor', 'qual': 'M.Tech (NIT Jaipur)', 'spec': 'Textile Auxiliaries, Specialty Chemicals', 'email': 'vivek.saxena@mit.edu', 'phone': '+919810015004', 'exp': '5 years', 'classes': ['TC-Sem 7', 'TC-Sem 8']},
    {'emp': 'TC005', 'first': 'Ritu', 'last': 'Agarwal', 'desig': 'assistant_professor', 'qual': 'M.Tech (IIT Delhi)', 'spec': 'Sustainable Textiles, Eco-friendly Processing', 'email': 'ritu.agarwal@mit.edu', 'phone': '+919810015005', 'exp': '4 years', 'classes': ['TC-Sem 3', 'TC-Sem 4', 'TC-Sem 6']},

    # MMFT (Man-Made Fiber Technology)
    {'emp': 'MMFT001', 'first': 'Ashok', 'last': 'Verma', 'desig': 'professor_hod', 'qual': 'Ph.D. (IIT Delhi)', 'spec': 'Melt Spinning, Polymer Rheology', 'email': 'ashok.verma@mit.edu', 'phone': '+919810016001', 'exp': '17 years', 'classes': ['MMFT-Sem 1', 'MMFT-Sem 2', 'MMFT-Sem 3']},
    {'emp': 'MMFT002', 'first': 'Kavita', 'last': 'Shah', 'desig': 'associate_professor', 'qual': 'Ph.D. (NIT Warangal)', 'spec': 'Specialty Fibers, Nanocomposites', 'email': 'kavita.shah@mit.edu', 'phone': '+919810016002', 'exp': '11 years', 'classes': ['MMFT-Sem 4', 'MMFT-Sem 5']},
    {'emp': 'MMFT003', 'first': 'Deepak', 'last': 'Jain', 'desig': 'assistant_professor', 'qual': 'M.Tech (IIT BHU)', 'spec': 'Bicomponent Fibers, Spunbond Technology', 'email': 'deepak.jain@mit.edu', 'phone': '+919810016003', 'exp': '6 years', 'classes': ['MMFT-Sem 5', 'MMFT-Sem 6']},
    {'emp': 'MMFT004', 'first': 'Sneha', 'last': 'Patil', 'desig': 'assistant_professor', 'qual': 'M.Tech (NIT Surat)', 'spec': 'Fiber Characterization, Testing', 'email': 'sneha.patil@mit.edu', 'phone': '+919810016004', 'exp': '5 years', 'classes': ['MMFT-Sem 7', 'MMFT-Sem 8']},
    {'emp': 'MMFT005', 'first': 'Rakesh', 'last': 'Yadav', 'desig': 'assistant_professor', 'qual': 'M.Tech (IIT Kanpur)', 'spec': 'Polymer Processing, Composite Materials', 'email': 'rakesh.yadav@mit.edu', 'phone': '+919810016005', 'exp': '4 years', 'classes': ['MMFT-Sem 3', 'MMFT-Sem 4', 'MMFT-Sem 6']},

    # Lab Assistants - CSE
    {'emp': 'CSE006', 'first': 'Ravi', 'last': 'Sharma', 'desig': 'lab_assistant', 'qual': 'B.Tech (NIT Patna)', 'spec': 'Computer Networks, DBMS, Operating Systems', 'email': 'ravi.sharma@mit.edu', 'phone': '+919810011006', 'exp': '8 years', 'classes': ['CSE-Sem 2', 'CSE-Sem 3', 'CSE-Sem 4', 'CSE-Sem 5']},
    {'emp': 'CSE007', 'first': 'Pooja', 'last': 'Kumari', 'desig': 'lab_assistant', 'qual': 'B.Tech (AKTU)', 'spec': 'Web Technologies, AI, Programming Labs', 'email': 'pooja.kumari@mit.edu', 'phone': '+919810011007', 'exp': '5 years', 'classes': ['CSE-Sem 1', 'CSE-Sem 6', 'CSE-Sem 7', 'CSE-Sem 8']},

    # Lab Assistants - ECE
    {'emp': 'ECE006', 'first': 'Vijay', 'last': 'Singh', 'desig': 'lab_assistant', 'qual': 'Diploma (Electronics)', 'spec': 'Analog & Digital Electronics, Embedded Systems', 'email': 'vijay.singh@mit.edu', 'phone': '+919810012006', 'exp': '10 years', 'classes': ['ECE-Sem 1', 'ECE-Sem 2', 'ECE-Sem 3', 'ECE-Sem 4']},
    {'emp': 'ECE007', 'first': 'Meena', 'last': 'Agarwal', 'desig': 'lab_assistant', 'qual': 'B.Tech (ECE)', 'spec': 'Communication Systems, VLSI, Microwave', 'email': 'meena.agarwal@mit.edu', 'phone': '+919810012007', 'exp': '6 years', 'classes': ['ECE-Sem 5', 'ECE-Sem 6', 'ECE-Sem 7', 'ECE-Sem 8']},

    # Lab Assistants - ME
    {'emp': 'ME006', 'first': 'Sohan', 'last': 'Lal', 'desig': 'lab_assistant', 'qual': 'Diploma (Mechanical)', 'spec': 'Workshop, Fluid Mechanics, Thermodynamics', 'email': 'sohan.lal@mit.edu', 'phone': '+919810013006', 'exp': '12 years', 'classes': ['ME-Sem 1', 'ME-Sem 2', 'ME-Sem 3', 'ME-Sem 4']},
    {'emp': 'ME007', 'first': 'Rekha', 'last': 'Devi', 'desig': 'lab_assistant', 'qual': 'B.Tech (Mechanical)', 'spec': 'CAD/CAM, Robotics, IC Engines Lab', 'email': 'rekha.devi@mit.edu', 'phone': '+919810013007', 'exp': '7 years', 'classes': ['ME-Sem 5', 'ME-Sem 6', 'ME-Sem 7', 'ME-Sem 8']},

    # Lab Assistants - TT
    {'emp': 'TT006', 'first': 'Mohan', 'last': 'Prasad', 'desig': 'lab_assistant', 'qual': 'B.Tech (Textiles)', 'spec': 'Yarn Manufacturing, Fabric Manufacturing', 'email': 'mohan.prasad@mit.edu', 'phone': '+919810014006', 'exp': '9 years', 'classes': ['TT-Sem 1', 'TT-Sem 2', 'TT-Sem 3', 'TT-Sem 4']},
    {'emp': 'TT007', 'first': 'Seema', 'last': 'Das', 'desig': 'lab_assistant', 'qual': 'B.Tech (Textiles)', 'spec': 'Textile Testing, Quality Control, Apparel Lab', 'email': 'seema.das@mit.edu', 'phone': '+919810014007', 'exp': '6 years', 'classes': ['TT-Sem 5', 'TT-Sem 6', 'TT-Sem 7', 'TT-Sem 8']},

    # Lab Assistants - TC
    {'emp': 'TC006', 'first': 'Rajesh', 'last': 'Kumar', 'desig': 'lab_assistant', 'qual': 'M.Sc. (Chemistry)', 'spec': 'Dyeing Lab, Analytical Chemistry, Water Testing', 'email': 'rajesh.kumar.tc@mit.edu', 'phone': '+919810015006', 'exp': '11 years', 'classes': ['TC-Sem 1', 'TC-Sem 2', 'TC-Sem 3', 'TC-Sem 4']},
    {'emp': 'TC007', 'first': 'Sangeeta', 'last': 'Roy', 'desig': 'lab_assistant', 'qual': 'B.Tech (TC)', 'spec': 'Textile Finishing, Printing, Nanotech Lab', 'email': 'sangeeta.roy@mit.edu', 'phone': '+919810015007', 'exp': '5 years', 'classes': ['TC-Sem 5', 'TC-Sem 6', 'TC-Sem 7', 'TC-Sem 8']},

    # Lab Assistants - MMFT
    {'emp': 'MMFT006', 'first': 'Dinesh', 'last': 'Kumar', 'desig': 'lab_assistant', 'qual': 'M.Sc. (Polymer Science)', 'spec': 'Polymer Characterization, Melt Spinning Lab', 'email': 'dinesh.kumar.mmft@mit.edu', 'phone': '+919810016006', 'exp': '9 years', 'classes': ['MMFT-Sem 1', 'MMFT-Sem 2', 'MMFT-Sem 3', 'MMFT-Sem 4']},
    {'emp': 'MMFT007', 'first': 'Asha', 'last': 'Singh', 'desig': 'lab_assistant', 'qual': 'B.Tech (MMFT)', 'spec': 'Fiber Testing, Composite Fabrication, Rheology Lab', 'email': 'asha.singh@mit.edu', 'phone': '+919810016007', 'exp': '6 years', 'classes': ['MMFT-Sem 5', 'MMFT-Sem 6', 'MMFT-Sem 7', 'MMFT-Sem 8']},
]


class Command(BaseCommand):
    help = 'Seed faculty data for all branches and semesters'

    def handle(self, *args, **options):
        existing_ids = set(Faculty.objects.values_list('employee_id', flat=True))

        class_map = {}
        for c in Class.objects.all():
            key = f'{c.name}-{c.section}'
            class_map[key] = c

        created = 0
        skipped = 0
        missing = set()
        for item in FACULTY_SEED:
            if item['emp'] in existing_ids:
                skipped += 1
                continue
            faculty = Faculty.objects.create(
                employee_id=item['emp'],
                first_name=item['first'],
                last_name=item['last'],
                designation=item['desig'],
                qualification=item['qual'],
                specialization=item['spec'],
                email=item['email'],
                phone=item['phone'],
                experience=item['exp'],
                is_active=True,
            )
            for cls_key in item['classes']:
                c = class_map.get(cls_key)
                if c:
                    faculty.classes.add(c)
                else:
                    missing.add(cls_key)
            created += 1

        self.stdout.write(self.style.SUCCESS(f'Created {created} faculty members ({skipped} already existed)'))
        if missing:
            self.stdout.write(self.style.WARNING(f'Missing classes: {", ".join(sorted(missing))}'))

from app.llm.privacy import redact

def test_known_names_student_ids_and_personal_contacts_removed():
 text='学生张三 ZZ999999999999 手机13812345678 邮箱abc@example.com 身份证110101199901011234'
 out=redact(text,{'张三':'【姓名001】'})
 for token in ['张三','ZZ999999999999','13812345678','abc@example.com','110101199901011234']:assert token not in out
 assert '【姓名001】'in out

def test_policy_numbers_and_public_landline_preserved():
 text='不少于5000字，截止2026年7月10日，校园应急电话0571-28881110'
 assert redact(text,{})==text

def test_anonymous_surrogate_is_retained_but_original_identifier_removed():
 # 已脱敏替身不能再当成原始敏感标识；不改变通用学号/手机/邮箱规则。
 text='张三 ZZ999999999999'
 out=redact(text,{'张三':'【姓名001】','ZZ999999999999':'【编号018】'})
 assert '张三'not in out and 'ZZ999999999999'not in out
 assert '【姓名001】'in out and '【编号018】'in out

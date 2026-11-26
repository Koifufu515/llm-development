from quarry.facts.extract import Stats,to_mentions

def test_repeated_price_is_matched_to_its_entity_not_model_output_order():
 text='1 金沙遗址博物馆。门票¥80。\n2 都江堰。门票¥80。'
 items=[dict(entity='都江堰',attribute='ticket_price',qualifier='全年',value='80',quote='¥80'),dict(entity='金沙遗址博物馆',attribute='ticket_price',qualifier='全年',value='80',quote='¥80')]
 rows=to_mentions(items,text,Stats())
 assert len(rows)==2
 assert rows[0]['span_start']==text.rindex('¥80')
 assert rows[1]['span_start']==text.index('¥80')

def test_duplicate_open_hours_stays_in_its_entry():
 text='石林。开放8:00-18:30。\n西山。开放8:00-18:30。\n翠湖公园。开放8:00-18:30。'
 raw=dict(entity='西山',attribute='open_hours',qualifier='全年',value='08:00-18:30',quote='8:00-18:30')
 r=to_mentions([raw],text,Stats())
 assert r[0]['span_start']==text.index('8:00-18:30',text.index('西山'))

def test_foreign_currency_is_not_a_rmb_ticket():
 raw=dict(entity='香港科学馆',attribute='ticket_price',qualifier='全年',value='20',quote='HKD$20')
 assert not to_mentions([raw],'香港科学馆。门票HKD$20。',Stats())

def test_entity_mentioned_in_other_entry_address_does_not_own_its_price():
 text='12 都江堰，地址四川省成都市都江堰景区，联系电话12345678，开放时间全天。门票¥80。\n13 青城山，地址四川都江堰市。门票¥80。'
 raw=dict(entity='都江堰',attribute='ticket_price',qualifier='全年',value='80',quote='¥80')
 assert to_mentions([raw],text,Stats())[0]['span_start']==text.index('¥80')

def test_transport_bundle_not_accepted_as_attraction_ticket():
 raw=dict(entity='通江街—湿地公园',attribute='ticket_price',qualifier='全年',value='98',quote='票价98元（包含湿地公园的门票）')
 assert not to_mentions([raw],'通江街—湿地公园\n票价98元（包含湿地公园的门票）',Stats())

def test_named_subattraction_price_cannot_be_assigned_to_parent():
 raw=dict(entity='西山',attribute='ticket_price',qualifier='全年',value='6',quote='华亭寺门票￥6')
 assert not to_mentions([raw],'西山。华亭寺门票￥6。',Stats())

def test_two_character_subattraction_name_not_parent():
 raw=dict(entity='西山',attribute='ticket_price',qualifier='全年',value='40',quote='龙门门票￥40')
 assert not to_mentions([raw],'西山。龙门门票￥40。',Stats())

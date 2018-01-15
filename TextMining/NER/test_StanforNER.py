# -*- coding: utf-8 -*-
import unittest
from StanfordNER import StanfordTagger
class TestTagger(unittest.TestCase):
	def test_case1(self):
		text = 'While in France, Christine Lagarde discussed short-term stimulus efforts in a recent interview with the Wall Street Journal.'
		st = StanfordTagger()
		classified_text = st.tag_text(text)

		print(classified_text)
		for t in classified_text:
			print(t[0])
			print(t[1])


	def test_case2(self):
		text = """Improving educational attainment across society is likely to have positive economic and social effects and the quest for knowledge and putting it to purposeful use is an important  part of the challenges that face European societies. In the last decade there has been a rapid growth of Massive Open Online Courses (MOOCs) predominantly from American universities in partnership with a number of foundations and private corporations that have enhanced the dominant position of English as the international language of academic life. However, there are many people who do not speak English and there is a large French speaking population around the world who can benefit from access to short courses of higher education.
                In response to the rise of MOOCs that use English, the French Ministry of National Education, Higher Education and Research committed an initial €20 million to a national digital education strategy that included the development of France Universite Numerique (FUN). It is a partnership of INRIA (a public sector institute for digital research), CINES (a public sector institute for ICT) and RENATER (a public interest group for telecommunications infrastructure) that is the national platform presented via a web portal. It also serves as an international portal for the Francophone world as MOOCs have been pioneered on a large scale in the English speaking world. FUN was launched in October 2013 and now has more than 750,000 registered users who have participated more than a million times in courses that now number nearly 200 from more than 60 partner institutions.
                The short courses cover a broad range of subjects and are all in French with some also offered in English to cater for the Anglophone world. FUN is part of a wider movement to promote a French-language international academic community and there is a broad mixture of users with the majority (61%) in the 25-50 age range, 13% are retired, 11% unemployed people and 9% are students showing the broad appeal of MOOCs. To register and take courses is free for users with modest fees for certification of completion and achievement. There are also plans for the development of MOOCs for vocational training to complement the academic and technical short courses that are currently on offer. As with all MOOC providers, the emphasis is on students interacting and learning from the presented sessions and from each other as well as completing the tasks that are required as part of the course.
                In relation to active ageing, FUN offers the MOOC experience to the French speaking population and should contribute to increasing educational attainment over the life course. It is interesting to note that it is used by a wide range of people showing that there is an enthusiasm for gaining knowledge for people of all ages. It is relevant to the active ageing indexs domain for the use of ICT and provides a powerful example of how learning is being transformed through the use of technology. While there are always risks of social innovations that rely on the use of ICT deepening the digital divide, the potential of MOOCs such as FUN to contribute to increasing educational attainment across the life course is very promising. There is a link between the level of educational attainment and employability over the life course so it is plausible that FUN can contribute to extending working lives as people learn new skills over their life course.
                """
		st = StanfordTagger()
		classified_text = st.tag_text(text)
		print(classified_text)
		for t in classified_text:
			print(t[0])
			print(t[1])

	def test_case3(self):
		text = """'
There are many areas of society and public policy that require innovations to be developed, tested and evaluated if we are to meet the challenges that we face. The Dutch government has embraced and encouraged innovation by establishing a network of 25 centres for expertise focusing on a particular issue ranging from biomass to craftsmanship to water technology. For the purposes of MOPACT, the most relevant is the Centre of Expertise for Healthy Ageing (CoE HA) which is a public-private partnership that acts as the hub for activities in the relevant policy area.
CoE HA was initially funded by a €4 million grant from the Ministry of Education and is based at Hanze Univeristy in Groningen. The focus is on a life course approach to healthy ageing that covers people of all ages with seven major thematic areas: active lifestyle and sports, eHealth and technology, healthy food, youth and lifestyle, living and leisure care, labour and care, welfare and health care. The CoE HA facilitates Innovation Workshops with partners from the public, private and voluntary/third sector in each of these thematic areas in order to develop innovative services and products. The aim is to foster partnerships by knowledge creation and exchange that can contribute to healthy ageing over the life course and create products and services for scaling up in the public sector, the market economy and civil society.
The CoE HA has five major functions starting with applied research through innovation workshops to develop solutions; health innovation that develops and tests new products and ways of working; educational development to support innovation; business development to support innovative ideas into flourishing businesses and disseminating information and awareness to professionals, policy makers, entrepreneurs, researchers and students about the potential for social innovation and healthy ageing. For example, in the active lifestyle and sports theme an innovation workshop to promote physical activity among older people developed a toolkit that could be used and a refresher training course for professionals. For active ageing diabetes, the innovation process focused on promoting a healthy and active lifestyle for people with pre-diabetes and the development of eHealth solutions and wearable technology to encourage physical activity.
An impressively wide range of social innovations across the thematic areas are underway and the CoE HA works with more than 160 partner organisations. These projects include eHealth and serious gaming for older people, exer-gaming for children with motor disabilities, the detection and prevention of clinical malnutrition in health care settings, improving the psycho-social treatments for children with dyslexia and ADHD, physical activity friendly design for public spaces and how workplace interventions can contribute to healthy ageing. The CoE HA has been sufficiently successful to move to a financially self-sustaining operation through fees from partners for the services it offers and it is at the cutting edge of active ageing in the Netherlands and beyond.
'"""
		st = StanfordTagger()
		classified_text = st.tag_text(text)
		print(classified_text)
		for t in classified_text:
			print(t[0])
			print(t[1])

	def test_case4(self):
		text = """I live on 130 Stretford street, M15 5JH, Manchester, UK"""
		st = StanfordTagger()
		classified_text = st.tag_text(text)
		print(classified_text)
		for t in classified_text:
			print(t[0])
			print(t[1])

if __name__=='main':
	unittest.main()
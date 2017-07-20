# -*- coding: utf-8 -*-
import sys
sys.path.append('gen-py')

import gflags
from keywords import FindKeywords
from keywords.ttypes import *

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

def print_keyword_list(keywords):
  sorted_keywords = sorted(keywords, key=lambda x: x.weight)
  for keyword in sorted_keywords:
    print keyword.term, keyword.weight, keyword.origin_format

def print_entity_list(entities):
  sorted_entities = sorted(entities, key=lambda x: x.weight)
  for entity in sorted_entities:
    print entity.origin_format, "---", entity.stem_format, entity.weight, entity.origin_score

if __name__ == '__main__':
  gflags.DEFINE_string("host", "0.0.0.0", "server host")
  gflags.DEFINE_integer("port", 6002, "server port")
  try:
     args = gflags.FLAGS(sys.argv)
  except gflags.FlagsError as err:
     print err
     sys.exit(err)
  host = gflags.FLAGS.host
  port = gflags.FLAGS.port

  news = News()
  news.url = "https://www.thequint.com/car-and-bike/2017/05/08/lexus-450d-launch-in-india-price-and-specifications"
  news.nid = "test_purpose_123456"
  news.title = "What does it mean that Donald Trump lost the debate?"
  news.main_content = '''Republican presidential candidate Doinald Trump. (Paul J. Richards/AFP/Getty Images) What does it mean that Donald Trump lost Monday night’s presidential debate? Sure, Trump had no real answer to Lester Holt’s point that economic conditions are, in fact, improving. Or Holt’s point that he carried on with his racist “birtherism” long after President Obama released his birth certificate. Or Holt’s point that he has no good reason to refuse to release his tax returns. Or Holt’s point that he said he favored the Iraq War in 2002. Or Hillary Clinton’s point that his fixation on trade agreements is myopic. Or Clinton’s point that his tax plan would increase the very national debt he has been railing against. Or Clinton’s point that experts predict his economic policies would throw the country into recession. Sure, Trump frequently interrupted and bullied Clinton before ranting about how she is the one with a temperament problem, eliciting a dismissive laugh from Clinton that was perhaps the most authentic expression of joy a politician has ever offered in a major-party presidential debate. Sure, he said some truly bizarre things, accusing Clinton of “fighting ISIS your entire adult life” and arguing that the United States should have required Iran to rein in North Korea in the nuclear deal. These and other moments made this a bad night for the Republican nominee. But none of them were surprising. We already knew that Trump is remarkably incurious about policy, boasting about how he does not listen to experts or read much. We already knew where that led him, to ideas such as igniting a trade war, reinstituting torture — worse than waterboarding — and killing the innocent children of suspected terrorists. We also already knew about his temperament — that Trump had engaged in racist attacks on a federal judge and dangerous stereotyping of American Muslims, including a gold star family. We already knew he regularly demeans people based on their appearance or physical disabilities. We also already knew that Trump is the most dishonest and least transparent presidential nominee in recent memory, refusing to release his tax returns even though every presidential nominee for 40 years has done so and betting that a visit to Dr. Oz relieved him of responsibility for releasing more information on his health. We already knew that he was an uncommon liar. The Post has only been the latest outlet to attempt to record the full panoply of deceptions Trump tells on a daily basis, such as his recent claims that Clinton has “been silent about Islamic terrorism for many years,” and that he “never” proposed targeting Muslims. The most surprising thing about the debate is that Trump entered it virtually tied with Clinton. It should have meant nothing. But, given where the polls are at the moment, I hope it means a lot. From here, the danger is that Clinton will get cocky and that Trump, who has shown he has some ability to adapt when he fails spectacularly, will get better in future debates. After all, if Americans were so evenly split heading into Monday night, after the monstrous campaign Trump had run before the debate, they may be capable of anything. '''
  news.meta_keywords = [u'debate', u'first', u'hillary', u'clinton', u'donald', u'trump', u'lost', u'won', u'winner', u'highlights', u'summary', u'wrapup', u'trade', u'polls', u'election', u'iraq', u'isis', u'muslims']

  news.title = "Big, Brawny, Blingy Lexus 450d SUV Launched at Rs 2.32 Crore"
  news.main_content = '''The Lexus 450d is almost like a luxury apartment on wheels. (Photo Courtesy: Lexus)_line_\xe2\x80\x9cYou can live in your car, but you can\xe2\x80\x99t drive your house!\xe2\x80\x9d That\xe2\x80\x99s the logic car enthusiasts sometimes give you for buying an incredibly expensive car. Especially one that costs as much as a luxury apartment. Like the Lexus 450d, that\xe2\x80\x99s almost like a luxury apartment on wheels and was launched recently at Rs 2.32 crore, ex-showroom Delhi._line_Lexus is Toyota\xe2\x80\x99s more expensive cousin. In March this year, Lexus announced its entry into India with a sedan and an SUV \xe2\x80\x93 the hybrid ES 300h sedan priced at Rs 55.27 lakh and the RX 450h priced at Rs 1.07 crore, ex-showroom Delhi. At that time, it also showcased the Lexus 450d, but had not put a price tag to it._line_The Lexus 450d is over 5 metres long. (Photo Courtesy: Lexus)_line_What\xe2\x80\x99s the Lexus 450d About?_line_This huge SUV with a rather confusing nomenclature is an uber-luxury cousin of the Toyota Land Cruiser. The over 200% import duties in India have ensured it gets a price tag that is rather astronomical. Yet, it has plenty of creature comforts and performance to kind of justify it._line_It weighs over 2.5 tonnes and boasts a mammoth 4.5-litre V8 diesel engine that pumps out 261 bhp of power and 650 Nm of torque with a six-speed automatic transmission and all-wheel drive. It can hit 100 kmph in about 8.6 seconds, clocking a top speed of 210 kmph._line_The interiors are draped in leather. (Photo: Lexus)_line_The design is pretty radical, with a sharp, angular front and triple-lens projector headlamps. The interiors are draped in beige and black leather, with an onboard 19-speaker infotainment system. There\xe2\x80\x99s also four-zone climate control, an air suspension to keep everyone comfortable, 10 airbags, traction control and terrain monitoring to keep everyone safe._line_A sunroof, moonroof, radar-based cruise control, a 12-inch screen, automatic lights and lane-departure warnings are all part of the package. And yes, it is pretty roomy, being over 5 metres long and with enough space for seven adults. Still thinking of buying an apartment?_line_ '''
  socket = TSocket.TSocket(host, port)
  transport = TTransport.TBufferedTransport(socket)
  protocol = TBinaryProtocol.TBinaryProtocol(transport)
  client = FindKeywords.Client(protocol)
  transport.open()

  result = client.find_keywords(news, 10)

  print "====== full keywords"
  print_keyword_list(result.full_keywords)

  print "====== title keywords"
  print_keyword_list(result.title_keywords)

  print "====== relevant entities"
  print_entity_list(result.relevant_entities)

  print "====== quality entities"
  print_entity_list(result.quality_entities)


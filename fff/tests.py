"""
unit tests
"""

from django.utils import unittest
from django.db import IntegrityError
from fff.models import *
from django.db import connection


def setUpModule():
    '''
    sets up test environment
    '''
    #creates tables unmanaged by modules
    #controlstatus table:
    rawsql = '''CREATE TABLE `fff_controlstatus`
(`id` int(11) NOT NULL AUTO_INCREMENT,
`control_id` int(11) NOT NULL,`output` varchar(2000) NOT NULL,
`errors` varchar(2000) DEFAULT NULL,`control_time` datetime NOT NULL,
`productionenvironment_id` int(11) DEFAULT NULL,
PRIMARY KEY (`id`),KEY `fff_controlstatus_6c17ffd4` (`control_id`)
) ENGINE=MEMORY AUTO_INCREMENT=3 DEFAULT CHARSET=latin1'''
    connection.cursor().execute(rawsql)
    # model used in TestCases:
    global host, user, pe, ts, control, pe, area, st, stat, cs, fs
    host = Host.objects.create(name='dell', ip='10.41.113.151')
    user = User.objects.create(name='ste')
    pe = ProductionEnvironment.objects.create(name='pe-dell', \
                                                  host=host, user=user)
    ts = TimeSlot.objects.create(start_time='00:00:00', end_time='06:00:00')
    control = Control.objects.create(name='test_control', script='test.pl', \
                                         time_slot=ts, threshold='test')
    area = Area.objects.create(name='test', productionEnvironment=pe)
    st = StatType.objects.create(name='test-stat')
    stat = Statistic.objects.create(stat_time='2012-01-01 00:00:00', \
                                        timestamp='2012-01-02 00:00:00', \
                                        stat_element='test-stat', \
                                        stat_value=1, \
                                        stat_extra='extra', statType=st, \
                                        productionEnvironment=pe)
    cs = ControlStatus.objects.create(control=control, output='test-output', \
                                          errors='test-errors', \
                                          control_time='2012-05-22 12:00:00', \
                                          productionEnvironment=pe)
    fs = FileServe.objects.create(file_name='test-file', \
                                      file_path='test-path', \
                                      destination_path='test-dest-path', \
                                      productionEnvironment=pe, \
                                      permissions='777', \
                                      error=False)


def tearDownModule():
    '''
    clears objects created in setup phase
    '''
    host.delete()
    user.delete()
    pe.delete()
    ts.delete()
    control.delete()
    area.delete()
    st.delete()
    stat.delete()


class HostTestCase(unittest.TestCase):
    '''
    unit test for Host model
    '''

    def test_unicode(self):
        self.assertEqual(host.__unicode__(), 'dell-10.41.113.151')

    def test_model_consistency(self):
        # same name
        self.assertRaisesRegexp(IntegrityError, Host.objects.create, \
                                    name='dell', ip='10.41.113.152')
        # same IP
        self.assertRaisesRegexp(IntegrityError, Host.objects.create, \
                                    name='dell1', ip='10.41.113.151')
        # same name, same IP
        self.assertRaisesRegexp(IntegrityError, Host.objects.create, \
                                    name='dell', ip='10.41.113.151')


class UserTestCase(unittest.TestCase):
    '''
    unit test for User model
    '''

    def test_unicode(self):
        '''
        tests if __unicode__() is working
        '''
        self.assertEqual(user.__unicode__(), 'ste')

    def test_model_consistency(self):
        # same name
        self.assertRaisesRegexp(IntegrityError, \
                                    User.objects.create, name='ste')


class ProductionEnvironmentTestCase(unittest.TestCase):
    '''
    unit test for ProductionEnvironment model
    '''

    def test_unicode(self):
        '''
        tests if __unicode__() is working
        '''
        self.assertEqual(pe.__unicode__(), 'pe-dell (dell-10.41.113.151 ste)')

    def test_model_consistency(self):
        self.host2 = Host.objects.create(name='dell2', ip='10.41.113.152')
        # same name, different host, same user -> OK
        self.pe2 = ProductionEnvironment.objects.create(name='pe-dell', \
                                                            host=self.host2, \
                                                            user=user)
        self.assertEqual(self.pe2.__unicode__(), \
                             'pe-dell (dell2-10.41.113.152 ste)')
        self.pe2.delete()
        self.host2.delete()
        # same name, same host, different user -> OK
        self.user2 = User.objects.create(name='ste2')
        self.pe3 = ProductionEnvironment.objects.create(name='pe-dell', \
                                                            host=host, \
                                                            user=self.user2)
        self.assertEqual(self.pe3.__unicode__(), \
                             'pe-dell (dell-10.41.113.151 ste2)')
        self.pe3.delete()
        self.user2.delete()
        # different name, same host, same user -> NOK
        self.assertRaisesRegexp(IntegrityError, \
                                    ProductionEnvironment.objects.create, \
                                    name='pe-dell2', host=host, user=user)
        # same name, same host, same user -> NOK
        self.assertRaisesRegexp(IntegrityError, \
                                    ProductionEnvironment.objects.create, \
                                    name='pe-dell', host=host, user=user)


class TimeSlotTestCase(unittest.TestCase):
    '''
    unit test for TimeSlot model
    '''

    def test_unicode(self):
        '''
        tests if __unicode__() is working
        '''
        self.assertEqual(ts.__unicode__(), '00:00:00 - 06:00:00')

    def test_model_consistency(self):
        # same start_time, different end_time -> OK
        self.ts2 = TimeSlot.objects.create(start_time='00:00:00', \
                                               end_time='12:00:00')
        self.assertEqual(self.ts2.__unicode__(), '00:00:00 - 12:00:00')
        self.ts2.delete()
        # different start_time, same end_time -> OK
        self.ts3 = TimeSlot.objects.create(start_time='06:00:00', \
                                               end_time='12:00:00')
        self.assertEqual(self.ts3.__unicode__(), '06:00:00 - 12:00:00')
        self.ts3.delete()
        # same start_time, same end_time -> NOK
        self.assertRaisesRegexp(IntegrityError, TimeSlot.objects.create, \
                                    start_time='00:00:00', end_time='06:00:00')


class ControlTestCase(unittest.TestCase):
    '''
    unit test for Control model
    '''

    def test_unicode(self):
        '''
        tests if __unicode__() is working
        '''
        self.assertEqual(control.__unicode__(), \
                             'test_control:  (test.pl - 00:00:00 - 06:00:00)')

    def test_control_pe(self):
        # adding a second productionEnvironment to Control
        control.productionEnvironment.add(pe)
        control.save()
        self.assertEqual(control.productionEnvironment.all()\
                             [0].__unicode__(), \
                             'pe-dell (dell-10.41.113.151 ste)')

    def test_model_consistency(self):
        # same name, same script, same time_slot, different threshold -> NOK
        self.assertRaisesRegexp(IntegrityError, Control.objects.create, \
                                    name='test_control', script='test.pl', \
                                    time_slot=ts, threshold='test2')
        # same name, same script, different time_slot, same threshold -> OK
        self.ts2 = TimeSlot.objects.create(start_time='00:00:00', \
                                               end_time='12:00:00')
        self.control2 = Control.objects.create(name='test_control', \
                                                   script='test.pl', \
                                                   time_slot=self.ts2, \
                                                   threshold='test')
        self.assertEqual(self.control2.__unicode__(), \
                             'test_control:  (test.pl - 00:00:00 - 12:00:00)')
        self.control2.delete()
        self.ts2.delete()
        # same name, different script, same time_slot, same threshold -> OK
        self.control3 = Control.objects.create(name='test_control', \
                                                   script='test2.pl', \
                                                   time_slot=ts, \
                                                   threshold='test')
        self.assertEqual(self.control3.__unicode__(), \
                             'test_control:  (test2.pl - 00:00:00 - 06:00:00)')
        self.control3.delete()
        # different name, same script, same time_slot, same threshold -> OK
        self.control4 = Control.objects.create(name='test_control2', \
                                                   script='test.pl', \
                                                   time_slot=ts, \
                                                   threshold='test')
        self.assertEqual(self.control4.__unicode__(), \
                             'test_control2:  (test.pl - 00:00:00 - 06:00:00)')
        self.control4.delete()
        # same name, same script, same time_slot, same threshold -> NOK
        self.assertRaisesRegexp(IntegrityError, Control.objects.create, \
                                    name='test_control', script='test.pl', \
                                    time_slot=ts, threshold='test')


class AreaTestCase(unittest.TestCase):
    '''
    unit test for Area model
    '''

    def test_unicode(self):
        '''
        tests if __unicode__() is working
        '''
        self.assertEqual(area.__unicode__(), 'test')

    def test_model_consistency(self):
        # different name, no pe configured -> NOK
        self.assertRaisesRegexp(IntegrityError, \
                                    Area.objects.create, name='test2')
        # different name, same pe -> OK
        self.area2 = Area.objects.create(name='test2', \
                                             productionEnvironment=pe)
        self.area2.delete()
        # same name, different pe -> OK
        self.user2 = User.objects.create(name='ste2')
        self.pe2 = ProductionEnvironment.objects.create(name='pe-dell', \
                                                            host=host, \
                                                            user=self.user2)
        self.area2 = Area.objects.create(name='test', \
                                             productionEnvironment=self.pe2)
        self.assertEqual(self.area2.__unicode__(), 'test')
        self.user2.delete()
        self.pe2.delete()
        self.area2.delete()
        # same name, same pe -> NOK
        self.assertRaisesRegexp(IntegrityError, \
                                    Area.objects.create, \
                                    name='test', \
                                    productionEnvironment=pe)


class StatTypeTestCase(unittest.TestCase):
    '''
    unit test for StatType model
    '''
    def test_unicode(self):
        '''
        tests if __unicode__() is working
        '''
        self.assertEqual(st.__unicode__(), 'test-stat')

    def test_model_consistency(self):
        # different name -> OK
        self.st2 = StatType.objects.create(name='test-stat2')
        self.assertEqual(self.st2.__unicode__(), 'test-stat2')
        self.st2.delete()
        # same name -> NOK
        self.assertRaisesRegexp(IntegrityError, StatType.objects.create, \
                                    name='test-stat')


class StatisticTestCase(unittest.TestCase):
    '''
    unit test for Statistic model
    '''

    def test_unicode(self):
        '''
        tests if __unicode__() is working
        '''
        self.assertEqual(stat.__unicode__(), \
           'test-stat-2012-01-01 00:00:00-pe-dell (dell-10.41.113.151 ste)')

    def test_model_consistency(self):
        # different stat_time, same timestamp, same stat_element,
        # same stat_value, same stat_extra, same productionEnvironment -> OK
        self.stat2 = Statistic.objects.create(\
            stat_time='2012-01-01 12:00:00', \
            timestamp='2012-01-02 00:00:00', \
            stat_element='test-stat', stat_value=1, \
            stat_extra='extra', statType=st, \
            productionEnvironment=pe)
        self.assertEqual(self.stat2.__unicode__(), \
             'test-stat-2012-01-01 12:00:00-pe-dell (dell-10.41.113.151 ste)')
        self.stat2.delete()
        # same stat_time, different timestamp, same stat_element,
        # same stat_value, same stat_extra, same productionEnvironment -> NOK
        self.assertRaisesRegexp(IntegrityError, \
                                    Statistic.objects.create, \
                                    stat_time='2012-01-01 00:00:00', \
                                    timestamp='2012-01-02 12:00:00', \
                                    stat_element='test-stat', stat_value=1, \
                                    stat_extra='extra', statType=st, \
                                    productionEnvironment=pe)
        # same stat_time, same timestamp, different stat_element,
        # same stat_value, same stat_extra, same productionEnvironment -> OK
        self.stat2 = Statistic.objects.create(\
                stat_time='2012-01-01 00:00:00', \
                timestamp='2012-01-02 00:00:00', \
                stat_element='test-stat2', stat_value=1, \
                stat_extra='extra', statType=st, \
                productionEnvironment=pe)
        self.assertEqual(self.stat2.__unicode__(), \
            'test-stat2-2012-01-01 00:00:00-pe-dell (dell-10.41.113.151 ste)')
        self.stat2.delete()
        # same stat_time, same timestamp, same stat_element,
        # different stat_value, same stat_extra,
        # same productionEnvironment -> NOK
        self.assertRaisesRegexp(IntegrityError, Statistic.objects.create, \
                                    stat_time='2012-01-01 00:00:00', \
                                    timestamp='2012-01-02 00:00:00', \
                                    stat_element='test-stat', stat_value=2, \
                                    stat_extra='extra', statType=st, \
                                    productionEnvironment=pe)
        # same stat_time, same timestamp, same stat_element,
        # same stat_valute, different stat_extra,
        # same productionEnvironment -> NOK
        self.assertRaisesRegexp(IntegrityError, Statistic.objects.create, \
                                    stat_time='2012-01-01 00:00:00', \
                                    timestamp='2012-01-02 00:00:00', \
                                    stat_element='test-stat', stat_value=1, \
                                    stat_extra='extra2', statType=st, \
                                    productionEnvironment=pe)
        # same stat_time, same timestamp, same stat_element, same stat_value,
        # same stat_extra, different productionEnvironment -> OK
        self.user2 = User.objects.create(name='ste2')
        self.pe2 = ProductionEnvironment.objects.create(name='pe-dell', \
                                                            host=host, \
                                                            user=self.user2)
        self.stat2 = Statistic.objects.create(
            stat_time='2012-01-01 00:00:00', \
                timestamp='2012-01-02 00:00:00', \
                stat_element='test-stat', stat_value=1, \
                stat_extra='extra', statType=st, \
                productionEnvironment=self.pe2)
        self.assertEqual(self.stat2.__unicode__(), \
             'test-stat-2012-01-01 00:00:00-pe-dell (dell-10.41.113.151 ste2)')
        self.stat2.delete()
        self.user2.delete()
        self.pe2.delete()
        # same stat_time, same timestamp, same stat_element,
        # same stat_value, same stat_extra, same productionEnvironment -> NOK
        self.assertRaisesRegexp(\
            IntegrityError, \
                Statistic.objects.create, \
                stat_time='2012-01-01 00:00:00', \
                timestamp='2012-01-02 00:00:00', \
                stat_element='test-stat', stat_value=1, \
                stat_extra='extra', statType=st, \
                productionEnvironment=pe)


class ControlStatusTestCase(unittest.TestCase):
    '''
    unit test for ControlStatus model
    '''

    def test_unicode(self):
        '''
        tests if __unicode__() is working
        '''
        self.assertEqual(cs.__unicode__(), \
 'pe-dell (dell-10.41.113.151 ste) - 2012-05-22 12:00:00 - test_control')

    def test_model_consistency(self):
        # same control, same output, same errors,
        # same control_time, same pe -> NOK
        self.assertRaisesRegexp(\
            IntegrityError, \
                ControlStatus.objects.create, \
                control=control, \
                output='test-output', \
                errors='test-errors', \
                control_time='2012-05-22 12:00:00', \
                productionEnvironment=pe)
        # different control, same output,
        # same errors, same control_time, same pe -> OK
        self.control2 = Control.objects.create(\
            name='test_control2', \
                script='test.pl', \
                time_slot=ts, \
                threshold='test')
        self.cs2 = ControlStatus.objects.create(\
            control=self.control2, \
                output='test-output', \
                errors='test-errors', \
                control_time='2012-05-22 12:00:00', \
                productionEnvironment=pe)
        self.assertEqual(cs.__unicode__(), \
 'pe-dell (dell-10.41.113.151 ste) - 2012-05-22 12:00:00 - test_control')
        self.control2.delete()
        self.cs2.delete()
        # same control, different output, same errors,
        # same control_time, same pe -> NOK
        self.assertRaisesRegexp(\
            IntegrityError, \
                ControlStatus.objects.create, \
                control=control, \
                output='test-output2', \
                errors='test-errors', \
                control_time='2012-05-22 12:00:00', \
                productionEnvironment=pe)
        # same control, same output, different errors,
        # same control_time, same pe -> NOK
        self.assertRaisesRegexp(\
            IntegrityError, \
                ControlStatus.objects.create, control=control, \
                output='test-output', errors='test-errors2', \
                control_time='2012-05-22 12:00:00', productionEnvironment=pe)
        # same control, same output, same errors,
        # same control_time, different pe -> OK
        self.user2 = User.objects.create(name='ste2')
        self.pe2 = ProductionEnvironment.objects.create(\
            name='pe-dell2', host=host, user=self.user2)
        self.cs2 = ControlStatus.objects.create(\
            control=control, output='test-output', \
                errors='test-errors', \
                control_time='2012-05-22 12:00:00', \
                productionEnvironment=self.pe2)
        self.assertEqual(self.cs2.__unicode__(), \
'pe-dell2 (dell-10.41.113.151 ste2) - 2012-05-22 12:00:00 - test_control')
        self.cs2.delete()
        self.user2.delete()
        self.pe2.delete()


class FileServeTestCase(unittest.TestCase):
    '''
    unit test for FileServe model
    '''

    def test_unicode(self):
        '''
        tests if __unicode__() is working
        '''
        self.assertEqual(fs.__unicode__(), 'test-path/test-file')

    def test_model_consistency(self):
        # same file_name, same file_path, same destination_path,
        # same pe, same permissions, same error -> NOK
        self.assertRaisesRegexp(\
            IntegrityError, \
                FileServe.objects.create, \
                file_name='test-file', \
                file_path='test-path', \
                destination_path='test-dest-path', \
                productionEnvironment=pe, \
                permissions='777', \
                error=False)
        # different file_name, same file_path, same destination_path,
        # same pe, same permissions, same error -> OK
        self.fs2 = FileServe.objects.create(\
            file_name='test-file2', file_path='test-path', \
                destination_path='test-dest-path', \
                productionEnvironment=pe, \
                permissions='777', \
                error=False)
        self.assertEqual(self.fs2.__unicode__(), 'test-path/test-file2')
        self.fs2.delete()
        # same file_name, different file_path, same destination_path,
        # same pe, same permissions, same error -> OK
        self.fs2 = FileServe.objects.create(\
            file_name='test-file', file_path='test-path2', \
                destination_path='test-dest-path', \
                productionEnvironment=pe, \
                permissions='777', \
                error=False)
        self.assertEqual(self.fs2.__unicode__(), 'test-path2/test-file')
        self.fs2.delete()
        # same file_name, same file_path, different destination_path,
        # same pe, same permissions, same error -> OK
        self.fs2 = FileServe.objects.create(\
            file_name='test-file', \
                file_path='test-path', \
                destination_path='test-dest-path2', \
                productionEnvironment=pe, \
                permissions='777', \
                error=False)
        self.assertEqual(self.fs2.__unicode__(), 'test-path/test-file')
        self.fs2.delete()
        # same file_name, same file_path, same destination_path,
        # different pe, same permissions, same error -> OK
        self.user2 = User.objects.create(name='ste2')
        self.pe2 = ProductionEnvironment.objects.create(\
            name='pe-dell2', host=host, user=self.user2)
        self.fs2 = FileServe.objects.create(\
            file_name='test-file', file_path='test-path', \
                destination_path='test-dest-path', \
                productionEnvironment=self.pe2, \
                permissions='777', \
                error=False)
        self.assertEqual(self.fs2.__unicode__(), 'test-path/test-file')
        self.fs2.delete()
        self.user2.delete()
        self.pe2.delete()
        # same file_name, same file_path, same destination_path,
        # same pe, different permissions, same error -> NOK
        self.assertRaisesRegexp(\
            IntegrityError, FileServe.objects.create, file_name='test-file', \
                file_path='test-path', \
                destination_path='test-dest-path', \
                productionEnvironment=pe, \
                permissions='666', \
                error=False)
        # same file_name, same file_path, same destination_path,
        # same pe, same permissions, different error -> NOK
        self.assertRaisesRegexp(\
            IntegrityError, FileServe.objects.create, file_name='test-file', \
                file_path='test-path', \
                destination_path='test-dest-path', \
                productionEnvironment=pe, \
                permissions='777', \
                error=True)

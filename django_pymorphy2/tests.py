from unittest import TestCase
from django import template
from django.utils.translation import ugettext_lazy as _

from six import PY3
from .templatetags.pymorphy_tags import inflect, plural, inflect_marked, inflect_collocation


class PymorphyDjangoTestCase(TestCase):
    def _msg(self, fmt, w1, w2):
        if PY3:
            return None

        # console fix for python 2
        return fmt.encode('utf8') % (w1.encode('utf8'), w2.encode('utf8'))


class InflectMarkedTagTest(PymorphyDjangoTestCase):

    def assertInflected(self, phrase, form, result):
        inflected_word = inflect_marked(phrase, form)
        err_msg = self._msg("%s != %s", inflected_word, result)
        self.assertEqual(inflected_word, result, err_msg)

    def test_basic_no_inflect(self):
        self.assertInflected('[[лошадь]] Пржевальского', 'дт', 'лошади Пржевальского')
        self.assertInflected('Москва', 'пр', 'Москва')
        self.assertInflected('[[Москва]]', 'пр', 'Москве')
        self.assertInflected('[[Москва]]-сити', 'пр', 'Москве-сити')

    def test_two_words_no_inflect(self):
        self.assertInflected('[[лошадь]] Пржевальского и [[красный конь]] Кузьмы Петрова-Водкина',
                             'дт',
                             'лошади Пржевальского и красному коню Кузьмы Петрова-Водкина')


class InflectTagTest(PymorphyDjangoTestCase):

    def assertInflected(self, phrase, form, result):
        inflected_word = inflect(phrase, form)
        err_msg = self._msg("%s != %s", inflected_word, result)
        self.assertEqual(inflected_word, result, err_msg)

    def test_word_case(self):
        self.assertInflected('Котопес', '', 'Котопес')
        self.assertInflected('ВАСЯ', '', 'ВАСЯ')
        self.assertInflected('котопес', '', 'котопес')

    def test_one_word(self):
        self.assertInflected('Москва', 'пр', 'Москве')
        self.assertInflected('бутявка', 'мн,тв', 'бутявками')
        self.assertInflected('Петрович', 'дт,отч', 'Петровичу')

        self.assertInflected('Петров', 'пр,имя,ед', 'Петре')
        self.assertInflected('Петрович', 'пр,отч,мн', 'Петровичах')

    def test_susliki(self):
        self.assertInflected('сусликов', 'тв', 'сусликами')

    def test_complex_phrase(self):
        self.assertInflected('тридцать восемь попугаев и Удав', 'дт',
                             'тридцати восьми попугаям и Удаву')
        self.assertInflected('Пятьдесят девять сусликов', 'тв', 'Пятьюдесятью девятью сусликами')

    def test_name(self):
        self.assertInflected('Геннадий Петрович', 'вн', 'Геннадия Петровича')
        self.assertInflected('Геннадий Петрович', 'дт', 'Геннадию Петровичу')
        self.assertInflected('Геннадий Петрович', 'тв', 'Геннадием Петровичем')
        self.assertInflected('Геннадий Петрович', 'пр', 'Геннадии Петровиче')

    def test_hyphen(self):
        self.assertInflected('Ростов-на-Дону', 'пр', 'Ростове-на-Дону')

    # тесты для несклоняемых кусков
    def test_basic_no_inflect(self):
        self.assertInflected('лошадь [[Пржевальского]]', 'дт', 'лошади Пржевальского')
        self.assertInflected('[[Москва]]', 'пр', 'Москва')
        self.assertInflected('Москва', 'пр', 'Москве')
        self.assertInflected('Москва[[-сити]]', 'пр', 'Москве-сити')

    def test_two_words_no_inflect(self):
        self.assertInflected('лошадь [[Пржевальского]] и красный конь [[Кузьмы Петрова-Водкина]]',
                             'дт',
                             'лошади Пржевальского и красному коню Кузьмы Петрова-Водкина')


class InflectCollocationTest(PymorphyDjangoTestCase):

    def assertInflected(self, phrase, form, result):
        inflected_word = inflect_collocation(phrase, form)
        err_msg = self._msg("%s != %s", inflected_word, result)
        self.assertEqual(inflected_word, result, err_msg)

    def test_one_word(self):
        self.assertInflected('Москва', 'пр', 'Москве')
        self.assertInflected('охота', 'вн', 'охоту')
        self.assertInflected('бутявка', 'мн,тв', 'бутявками')
        self.assertInflected('Петрович', 'дт,отч', 'Петровичу')

        # Т. к. мы берём в работу только слова в Именительном падеже,
        # вместо имени Петр (Петров - родительный падеж) обрабатывается фамилия Петров
        # соответственно форма 'имя' здесь не учитывается
        # см. аналогичный тест выше в InflectTagTest
        self.assertInflected('Петров', 'пр,имя,ед', 'Петрове')
        # Но для именительного всё работает как надо
        self.assertInflected('Петры', 'пр,имя,ед', 'Петре')
        self.assertInflected('Петрович', 'пр,отч,мн', 'Петровичах')

    def test_not_nomn_forms(self):
        self.assertInflected('Отдыха', 'им', 'Отдыха')
        self.assertInflected('дров', 'дт', 'дров')

    def test_collocation(self):
        self.assertInflected('База отдыха', 'тв', 'Базой отдыха')
        self.assertInflected('База отдыха', 'рд', 'Базы отдыха')
        self.assertInflected('куча дров', 'рд', 'кучи дров')

        self.assertInflected('зимняя рыбалка', 'вн', 'зимнюю рыбалку')
        self.assertInflected('корпоративный отдых', 'вн', 'корпоративный отдых')
        self.assertInflected('экологические туры', 'вн', 'экологические туры')
        self.assertInflected('семейный отдых', 'вн', 'семейный отдых')

        self.assertInflected('Сигизмунд Петрович', 'вн', 'Сигизмунда Петровича')
        self.assertInflected('Летящий на параплане', 'пр', 'Летящем на параплане')
        self.assertInflected('Летящий на параплане', 'тв', 'Летящим на параплане')

        self.assertInflected('Пакет с пряниками', 'рд', 'Пакета с пряниками')

        self.assertInflected('деревня Самосделкино', 'вн', 'деревню Самосделкино')


class PluralTagTest(PymorphyDjangoTestCase):
    def assertPlural(self, phrase, amount, result):
        morphed = plural(phrase, amount)
        err_msg = self._msg("%s != %s", morphed, result)
        self.assertEqual(morphed, result, err_msg)

    def test_pluralize(self):
        self.assertPlural('бутявка', 1, 'бутявка')
        self.assertPlural('бутявка', 2, 'бутявки')
        self.assertPlural('бутявка', 5, 'бутявок')
        self.assertPlural('Бутявка', 1, 'Бутявка')

    def test_phrase(self):
        self.assertPlural('Геннадий Петрович', 8, 'Геннадиев Петровичей')

    def test_mixed(self):
        self.assertPlural('активный пользователь', 1, 'активный пользователь')
        self.assertPlural('активный пользователь', 2, 'активных пользователя')
        self.assertPlural('активный пользователь', 3, 'активных пользователя')
        self.assertPlural('активный пользователь', 4, 'активных пользователя')
        self.assertPlural('активный пользователь', 5, 'активных пользователей')
        self.assertPlural('активный пользователь', 10, 'активных пользователей')
        self.assertPlural('активный пользователь', 21, 'активный пользователь')


class LazyStringTest(PymorphyDjangoTestCase):

    def test_safe_string(self):
        tpl = template.Template("{% load pymorphy_tags %}{{ 'конь'|inflect:'дт' }}")
        rendered, expected = tpl.render(template.Context()), 'коню'
        err_msg = self._msg("%s != %s", rendered, expected)
        self.assertEqual(rendered, expected, err_msg)

    def test_i18n_string(self):
        horse = _('конь')
        tpl = template.Template("{% load pymorphy_tags %}{{ horses|inflect:'дт' }}")
        rendered, expected = tpl.render(template.Context({'horses': horse})), 'коню'
        err_msg = self._msg("%s != %s", rendered, expected)
        self.assertEqual(rendered, expected, err_msg)

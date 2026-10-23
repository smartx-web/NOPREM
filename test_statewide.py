"""Statewide adaptation checks using disposable sample records only."""
import unittest
import app
import auth
import access
from locations import LGAS
import test_app


class StatewideTests(unittest.TestCase):
    setUp = test_app.PortalTests.setUp
    tearDown = test_app.PortalTests.tearDown

    def test_all_23_lgas_persist_and_filter(self):
        self.assertEqual(len(set(LGAS)), 23)
        for index, lga in enumerate(LGAS):
            app.save('pu', dict(self.pu, lga=lga, code=f'SAMPLE-{index}'))
        with app.connect() as db:
            self.assertEqual({row[0] for row in db.execute('SELECT lga FROM pus')}, set(LGAS))
        for lga in LGAS:
            _, units, _, _, _ = app.filtered_records(dict(lga=lga))
            self.assertEqual([unit['lga'] for unit in units], [lga])
        with self.assertRaises(ValueError):
            app.save('pu', dict(self.pu, lga='Outside Benue', code='BAD'))

    def test_statewide_coordinator_scope_does_not_widen_access(self):
        app.save('pu', dict(self.pu, lga='Makurdi', code='SAMPLE-MAK'))
        app.save('pu', dict(self.pu, lga='Gboko', code='SAMPLE-GBK'))
        with app.connect() as db:
            account_id = auth.manage_account(db, dict(username='sample-coordinator',
                role='coordinator', lga='Makurdi', wards='', active='yes',
                password='sample-test-password-only'), None)
            user = auth.user_snapshot(db.execute('SELECT * FROM users WHERE id=?', (account_id,)).fetchone())
        token = access.current_user.set(user)
        try:
            all_units, *_ = app.filtered_records({})
            self.assertEqual([unit['lga'] for unit in all_units], ['Makurdi'])
            with self.assertRaises(PermissionError):
                app.save('report', dict(pu_id='2', category='Logistics', detail='Sample'))
        finally:
            access.current_user.reset(token)

    def test_branding_and_empty_lgas_are_reserved(self):
        page = app.page()
        self.assertIn('Better Benue 2027', page)
        self.assertIn('Apa and Agatu only', page)
        self.assertIn('Official portrait or logo to be supplied', page)
        for lga in LGAS:
            self.assertIn(f'value="{lga}"', page)
        login = auth.login_page('sample-csrf')
        self.assertNotIn('solomon.jpg', login)
        self.assertNotIn('Engr. Solomon', login)


if __name__ == '__main__':
    unittest.main()

import unittest
import json
from app.main import app, db, Task, User

class TaskManagerTestCase(unittest.TestCase):

    def setUp(self):
        # Configure app for testing
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

        # Create a new test client
        self.app = app.test_client()

        with app.app_context():
            # Drop everything first to ensure clean slate (if reusing engine)
            db.drop_all()
            db.create_all()

            # Create Users
            admin = User(username='admin', email='admin@example.com', role='Admin')
            staff = User(username='staff', email='staff@example.com', role='Staff')

            db.session.add(admin)
            db.session.add(staff)

            # Add initial task
            task = Task(
                title='Task 1',
                description='Desc 1',
                assignee='staff',
                assignee_email='staff@example.com',
                due_date='2023-12-31',
                status='Todo'
            )
            db.session.add(task)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def login_as(self, username):
        # Helper to simulate login session
        with app.app_context():
            user = User.query.filter_by(username=username).first()
            if user:
                with self.app.session_transaction() as sess:
                    sess['user_id'] = user.id

    def test_index_redirects_if_not_logged_in(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)

    def test_index_logged_in(self):
        self.login_as('admin')
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Team Task Manager', response.data)

    def test_get_tasks(self):
        self.login_as('staff')
        response = self.app.get('/tasks')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['tasks']), 1)
        self.assertEqual(data['tasks'][0]['title'], 'Task 1')

    def test_add_task(self):
        self.login_as('admin')
        new_task = {
            'title': 'New Task',
            'description': 'New Desc',
            'assignee': 'staff',
            'assignee_email': 'staff@example.com',
            'due_date': '2024-01-01'
        }
        response = self.app.post('/tasks', data=json.dumps(new_task), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['task']['title'], 'New Task')

        # Verify DB
        with app.app_context():
            tasks = Task.query.all()
            self.assertEqual(len(tasks), 2)

    def test_update_task(self):
        self.login_as('staff')
        update_data = {'status': 'Done'}
        response = self.app.put('/tasks/1', data=json.dumps(update_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

        with app.app_context():
            task = db.session.get(Task, 1)
            self.assertEqual(task.status, 'Done')

    def test_delete_task(self):
        self.login_as('admin')
        response = self.app.delete('/tasks/1')
        self.assertEqual(response.status_code, 200)

        with app.app_context():
            tasks = Task.query.all()
            self.assertEqual(len(tasks), 0)

    def test_add_user_admin(self):
        self.login_as('admin')
        new_user = {'username': 'newstaff', 'role': 'Staff'}
        response = self.app.post('/api/users', data=json.dumps(new_user), content_type='application/json')
        self.assertEqual(response.status_code, 201)

        with app.app_context():
            user = User.query.filter_by(username='newstaff').first()
            self.assertIsNotNone(user)

    def test_add_user_forbidden_staff(self):
        self.login_as('staff')
        new_user = {'username': 'hacker', 'role': 'Admin'}
        response = self.app.post('/api/users', data=json.dumps(new_user), content_type='application/json')
        self.assertEqual(response.status_code, 403)

if __name__ == '__main__':
    unittest.main()

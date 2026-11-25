import requests


class BrightspaceAPI:
    def __init__(self, base_url, access_token):
        self.base_url = base_url.rstrip("/")
        self.lp_version = "1.64"
        self.le_version = "1.100"

        self.session = requests.Session()

        self.session.headers.update({
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        })

    def get(self, path, params=None):
        response = self.session.get(
            f"{self.base_url}{path}",
            params=params,
            timeout=30
        )

        response.raise_for_status()

        return response.json()

    def get_user(self):
        return self.get(
            f"/d2l/api/lp/{self.lp_version}/users/whoami"
        )

    def get_courses(self):
        courses = []
        bookmark = None

        while True:
            params = {}

            if bookmark:
                params["bookmark"] = bookmark

            data = self.get(
                f"/d2l/api/lp/{self.lp_version}/enrollments/myenrollments/",
                params=params
            )

            for item in data["Items"]:
                if item["OrgUnit"]["Type"]["Code"] == "Course Offering":
                    courses.append(item)

            paging = data["PagingInfo"]

            if not paging["HasMoreItems"]:
                break

            bookmark = paging["Bookmark"]

        return courses

    def get_grades(self, course_id):
        return self.get(
            f"/d2l/api/le/{self.le_version}/{course_id}/grades/values/myGradeValues/"
        )

    def get_grade_categories(self, course_id):
        return self.get(
            f"/d2l/api/le/{self.le_version}/{course_id}/grades/categories/"
        )

    def get_assignments(self, course_id):
        return self.get(
            f"/d2l/api/le/{self.le_version}/{course_id}/dropbox/folders/"
        )

    def get_submissions(self, course_id, assignment_id):
        return self.get(
            f"/d2l/api/le/{self.le_version}/{course_id}/dropbox/folders/"
            f"{assignment_id}/submissions/mysubmissions/"
        )

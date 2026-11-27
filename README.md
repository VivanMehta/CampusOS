# CampusOS

CampusOS is a full-stack academic management platform designed to centralize course information, assignment deadlines, calendars, grades, and academic planning into a single workspace.

Built with React, TypeScript, Python, and Django, CampusOS integrates with Brightspace to retrieve and process academic data, providing students with an alternative interface for managing their education.

## Features

### Academic Dashboard
- Centralized academic overview.
- Upcoming assignment deadlines and calendar events.
- Course and semester organization.
- Responsive dark-mode interface.

### Brightspace Integration
- iCalendar feed synchronization.
- Course enrollment importing.
- Grade and assignment data importing.
- Automatic course and semester identification.
- Duplicate prevention during repeated imports.

### Grade Tracking
- Categorized assessment breakdowns.
- Individual assessment grades and percentages.
- Weighted course grade calculations.
- Assessment weight normalization.
- Distinction between ungraded assessments and zero marks.

### Grade Prediction
- Interactive final-grade target selection.
- Required average calculation for remaining assessments.
- Completed and remaining course weight tracking.
- Detection of unsupported grading configurations.

### Backend
- Authenticated REST API.
- Relational database architecture.
- User-specific academic records.
- Transaction-based data importing.
- Environment-based configuration.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, TypeScript |
| Backend | Python, Django |
| API | Django REST Framework |
| Database | SQLite |
| Styling | CSS, Tailwind CSS |
| Build Tool | Vite |
| HTTP Client | Axios |
| External Integration | Brightspace REST API, iCalendar |
| Version Control | Git, GitHub |

## Architecture

CampusOS separates external data integration, backend processing, persistent storage, and frontend presentation.

Brightspace data is processed through Python integration services and imported into a relational database. Django exposes the stored academic information through authenticated REST endpoints, which are consumed by the React frontend.

Grade calculations and predictions are performed client-side, allowing users to interact with their academic data without repeatedly contacting the backend.

## Project Structure

```text
CampusOS/
├── backend/
│   ├── academics/
│   │   ├── management/
│   │   │   └── commands/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── accounts/
│   ├── dashboard/
│   ├── config/
│   └── manage.py
├── frontend/
│   └── src/
│       ├── pages/
│       ├── services/
│       ├── utils/
│       └── App.tsx
├── integrations/
│   ├── providers/
│   └── brightspace.py
├── .gitignore
└── README.md
```

## Development Status

CampusOS is currently a functional development prototype.

The core backend, academic dashboard, calendar integration, course importing, grade tracking, and basic grade prediction engine have been implemented.

Calendar synchronization uses a private Brightspace calendar subscription. Course, grade, and assignment information currently relies on manually exported Brightspace API responses.

Automatic account authentication and full academic synchronization are planned for future development.

Grade calculations are estimates and may not account for every institutional grading configuration.

## Roadmap

- [x] Django backend and relational database
- [x] Authenticated REST API
- [x] React dashboard
- [x] Brightspace calendar synchronization
- [x] Course and semester importing
- [x] Grade and assignment importing
- [x] Weighted grade calculation engine
- [x] Interactive grade predictor
- [ ] Authorized Brightspace OAuth integration
- [ ] Automatic academic synchronization
- [ ] Assignment completion tracking
- [ ] Individual course detail pages
- [ ] Advanced grading configuration support
- [ ] Automated testing
- [ ] Production deployment

## Privacy and Security

CampusOS is designed to keep academic information separate from the application's source code.

Sensitive configuration, authentication credentials, local databases, and personal academic exports should remain excluded from version control.

Academic API endpoints require authentication and restrict records to their respective users.

## Project Purpose

CampusOS was developed as an independent software engineering project to explore full-stack application development, external API integration, relational database design, data processing, authentication, and interactive mathematical algorithms.

## Disclaimer

CampusOS is an independent project and is not affiliated with, endorsed by, or officially supported by D2L, Brightspace, or any educational institution.

## Author

**Vivan Mehta**

Software Development Student — Southern Alberta Institute of Technology (SAIT)

[GitHub](https://github.com/VivanMehta) · [LinkedIn](https://www.linkedin.com/in/vivan-mehta-a43ba5293/)

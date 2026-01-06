# Changelog

All notable changes to the Fitness Dashboard project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Documentation refresh with updated user guide visuals and corrected repository links

## [0.1.0] - 2025-10-26

### Added
- Comprehensive audit history system for workout classification tracking
- ML model versioning and registry system with performance metrics
- User classification feedback collection for model improvement
- Batch audit logging capabilities for performance optimization
- Model lineage tracking with parent-child relationships
- Classification persistence tables for fast lookups
- Model activation and status management system
- Audit service (`src/services/audit_service.py`) for complete traceability
- Enhanced model manager v2 (`src/ml/model_manager_v2.py`) with integrated audit trail
- Database migration script for audit tables (`scripts/add_audit_tables.py`)
- Comprehensive audit and versioning documentation (`docs/developer/audit-and-versioning-guide.md`)

### Changed
- Updated main AI Intelligence view with enhanced layout and clarity
- Improved K-means scatter plot visualization with optimal scaling
- Redesigned cluster visualization with white background for maximum contrast
- Enhanced legend presentation (4 entries instead of 8) for cleaner display
- Optimized axis scaling with 15% padding and data percentile-based ranges
- Larger cluster center stars (size=25) with gold borders for better visibility
- Opacity-based period distinction (solid=current, faded=historical workouts)
- Increased chart height to 550px for better visualization
- Enhanced hover tooltips with period labels
- Improved consistency analysis styling for better comprehension

### Fixed
- K-means visualization bug showing duplicate cluster centers in legend
- Missing Real Run center star in cluster visualization
- Cluster center calculation now based on actual data centroids, not just K-means assignments
- Deduplicated cluster centers by activity type to prevent multiple stars for same category
- Requirements file dependencies and path references

## [0.0.9] - 2025-09-25

**Production Deployment Release** 🚀

### Added
- Production deployment tag (`deploy-2025-09-25-1925`)
- Sessions database cleanup and `.gitignore` updates

### Changed
- Updated relative path handling for `update_db.py` script
- Enhanced development workflow documentation

### Fixed
- Path resolution issues in `utilities.py` config module import
- Path resolution issues in `update_db.py` utils module import
- Documentation links throughout the project
- Data serialization error in Choco Effect dashboard
- Minor typos in documentation and user-facing text

## [0.0.8] - 2025-09-12

**Critical Stability Release**

### Fixed
- Resolved critical runtime errors affecting dashboard loading
- Enhanced error handling in database service
- Improved type conversion and null value handling
- Fixed DataFrame column existence checks
- Added defensive programming patterns throughout codebase

### Changed
- Enhanced development workflow with better error messages
- Improved debugging capabilities for Streamlit pages

### Added
- Comprehensive error handling documentation in `CLAUDE.md`
- Debugging and error handling best practices guide
- Development mode testing guidelines

## [0.0.7] - 2025-09-10

**Intelligence Platform Phase 2 Release** 🧠

### Added
- **Intelligence-First Interface**
  - Intelligence Dashboard as primary landing page
  - Daily Intelligence Brief with personalized AI-generated insights
  - Focus Area Determination using multi-dimensional consistency analysis
  - Real-time Trending Analysis with statistical confidence scoring
  - Performance Alerts through advanced anomaly detection

- **Complete Algorithm Transparency System**
  - Source code traceability - every AI insight links to implementation (file:line)
  - Interactive algorithm explorer with expandable explanation cards
  - Algorithm Registry tracking all AI systems with performance metrics
  - User feedback integration for continuous AI improvement
  - Confidence visualization with color-coded certainty indicators (0-100%)

- **Advanced Machine Learning Classification**
  - K-means workout categorization (87% accuracy, <5s for 1K workouts)
  - Automatic classification into real_run, choco_adventure, mixed, outlier categories
  - Confidence scoring based on distance to cluster centers
  - Multi-feature analysis using pace, distance, and duration patterns

- **Statistical Intelligence Engine**
  - Linear regression trend analysis with p-value confidence intervals
  - Multi-method anomaly detection (IQR, Z-score, Modified Z-score)
  - Performance forecasting with uncertainty quantification
  - Consistency scoring across frequency, timing, performance, and streak dimensions

- **New Services and Utilities**
  - `src/services/intelligence_service.py` - Central AI orchestration
  - `src/utils/consistency_analyzer.py` - Multi-dimensional consistency scoring
  - Enhanced `src/utils/statistics.py` - Advanced statistical analysis

- **Comprehensive Testing Infrastructure**
  - 200+ test methods across 6 specialized test suites
  - AI-specific testing patterns for ML model validation
  - Performance benchmarking with automated regression detection
  - Algorithm transparency verification ensuring traceability accuracy
  - Overall code coverage >90%, AI service coverage >95%

### Changed
- Navigation restructured with Intelligence section as primary
- UI transformation with progressive disclosure design
- Enhanced database service with AI integration
- Algorithm transparency integrated throughout interface

### Performance
- AI Classification: <5 seconds for 1,000+ workouts ✅
- Intelligence Brief Generation: <3 seconds ✅
- Algorithm Transparency Loading: <3 seconds ✅
- Statistical Analysis: <2 seconds for trend detection ✅
- Concurrent User Support: 10+ simultaneous requests
- Memory Optimization: <500MB for large dataset operations

## [0.0.6] - 2025-09-08

### Added
- SQL documentation validation tooling (`scripts/validate_sql_docs.py`)
- SQL query validation requirements and guidelines in documentation

### Fixed
- SQL documentation queries for MySQL 9.2.0 compatibility
- Reserved word alias issues in SQL examples
- GROUP BY compliance issues in documentation queries
- Dashboard datetime conversion issues after database rollback

### Changed
- Enhanced SQL documentation guidelines with validation requirements
- Improved MySQL compatibility for `sql_mode=only_full_group_by`

## [0.0.5] - 2025-09-07

**Choco Effect Dashboard Release** 🐕

### Added
- **The Choco Effect Portfolio Dashboard** - Specialized dashboard showcasing behavioral transformation
- Choco Effect Classifier with K-means clustering
- Era-based classification system with configurable Choco Effect Date (default: 2018-06-01)
- Smart fallback hierarchy: ML clustering → Era-based defaults → Rule-based classification
- Activity-specific insights in intelligence brief
- Enhanced intelligence brief with personalized recommendations
- Unified data filtering utilities (`src/utils/data_filters.py`)
- Visual Assets Table of Contents (`docs/VISUAL_ASSETS_TOC.md`)
- MCP Playwright testing integration documentation

### Changed
- Classification defaults based on pre/post-Choco era patterns
- Eliminated duplicate filtering between Intelligence Brief and View Selected Data
- Improved data consistency across all dashboard pages
- Enhanced user experience with clearer metrics and explanations

### Fixed
- Date consistency - all pages now use current date as reference for "days back" calculations
- Metric alignment between analyzed and displayed workouts

## [0.0.4] - 2025-08-24

**Architecture Restructure Release** 🏗️

### Added
- Comprehensive project restructuring with modular architecture
- New `src/config/` directory for environment-aware configuration
  - `database.py` - Database connection settings
  - `app.py` - Application configuration
  - `logging_config.py` - Logging setup
- New `src/services/` directory for business logic layer
  - `database_service.py` - Centralized database operations
- New `src/utils/` directory for analytics utilities
- Complete documentation overhaul with MkDocs
  - `docs/ai/` - AI/ML feature documentation
  - `docs/user-guide/` - End-user documentation
  - `docs/developer/` - Technical documentation
  - `docs/getting-started/` - Onboarding guides
  - `docs/reference/` - API and reference material

### Changed
- Reorganized project structure for better maintainability
- Separated concerns: configuration, services, views, and utilities
- Enhanced environment detection (Development on macOS, Production on Linux/AWS RDS)
- Improved database connection management

## [0.0.3] - 2025-04-25

**Production Deployment Support** 🌐

### Added
- AWS RDS production deployment configuration
- Environment variable support for RDS endpoints
- Automatic environment detection (Development vs Production)
- Deployment script (`scripts/deploy.sh`)
- Systemd service management for production
- `requirements.txt` for EC2 deployment (alongside Poetry)

### Changed
- Database connection logic to auto-select production/development mode
- Enhanced environment variable handling
- Reorganized Streamlit pages for better navigation

### Fixed
- Database connection bugs in fitness-overview page
- Environment variable configuration issues

## [0.0.2] - 2025-04-23

**Authentication Release** 🔐

### Added
- Session-based login system
- Authentication page (`src/views/login.py`)
- Session state management for user tracking
- Development mode bypass feature
  - `STREAMLIT_DEV_MODE=true` environment variable support
  - URL parameter `?dev_mode=true` for quick testing
  - Direct page access without authentication for testing

### Security
- Secure session handling
- Password authentication system
- Session timeout management

## [0.0.1] - 2025-04-18

**Initial Release** 🎉

### Added
- Core Streamlit multi-page application
- MySQL database backend integration
- CSV import pipeline for MapMyRun workout history
- Basic dashboard visualizations with Plotly
- Monthly workout statistics view
- Performance metrics tracking:
  - Distance (miles)
  - Duration (seconds)
  - Calories burned
  - Average and max pace
  - Steps
- Activity type breakdowns
- Calendar visualization with `streamlit-calendar`
- Interactive charts with `streamlit-plotly-events`
- Database initialization script (`scripts/init.py`)
- Database update script (`scripts/update_db.py`)
- Poetry dependency management setup
- Development environment configuration with direnv support
- Basic SQL query interface

### Technical Foundation
- Python 3.12+ support
- MySQL 8.0+ database schema
- Environment-aware configuration system
- Data validation and error handling
- Historical data browsing capabilities

---

## Release Notes Legend

### Categories
- **Added** - New features
- **Changed** - Changes in existing functionality
- **Deprecated** - Soon-to-be removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Security improvements
- **Performance** - Performance enhancements

### Semantic Versioning
- **MAJOR** version (X.0.0): Incompatible API changes
- **MINOR** version (0.X.0): New functionality (backward compatible)
- **PATCH** version (0.0.X): Bug fixes (backward compatible)

---

## Links

- [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
- [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
- [AI Features Changelog](docs/features/CHANGELOG_AI_FEATURES.md)
- [Project Documentation](docs/index.md)
- [Contributing Guidelines](docs/developer/contributing.md)

---

*Last Updated: 2025-10-26*
*Maintained by: Barbara Hidalgo-Shimizu*
*Repository: [github.com/dagny099/fitness-dashboard](https://github.com/dagny099/fitness-dashboard)*

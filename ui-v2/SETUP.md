# UI-V2 Project Setup Guide

This guide will help you set up the ui-v2 project on a new device, including all dependencies, database configuration, authentication, and development environment.

## Prerequisites

Before starting, ensure you have the following installed:

- **Node.js** (v18.18.0 or higher)
- **npm** or **pnpm** (recommended)
- **Git**
- **PostgreSQL** (v14 or higher) or access to a PostgreSQL database
- **VS Code** (recommended IDE)

## 1. Clone and Initial Setup

```bash
# Clone the repository
git clone https://github.com/cigna-group/e2e-ai.git
cd e2e-ai/ui-v2

# Install dependencies (using pnpm - recommended)
pnpm install

# Or using npm
npm install
```

## 2. Environment Configuration

Create the environment files:

```bash
# Copy the environment template
cp .env.example .env.local
```

Edit `.env.local` with your configuration:

```env
# Database Configuration
DATABASE_URL="postgresql://username:password@localhost:5432/e2e_ai_db"

# NextAuth.js Configuration
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="your-super-secret-key-here-minimum-32-characters"

# Development
NODE_ENV="development"
```

### Environment Variables Explained:

- **DATABASE_URL**: PostgreSQL connection string
- **NEXTAUTH_URL**: The base URL of your application
- **NEXTAUTH_SECRET**: A random secret used to encrypt tokens (generate a secure one)

## 3. Database Setup

### Option A: Local PostgreSQL

1. **Install PostgreSQL** if not already installed:
   - Windows: Download from [postgresql.org](https://www.postgresql.org/download/)
   - macOS: `brew install postgresql`
   - Linux: `sudo apt-get install postgresql postgresql-contrib`

2. **Create Database**:
```sql
-- Connect to PostgreSQL as superuser
psql -U postgres

-- Create database
CREATE DATABASE e2e_ai_db;

-- Create user (optional)
CREATE USER e2e_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE e2e_ai_db TO e2e_user;
```

### Option B: Cloud Database (Recommended for Production)

You can use services like:
- **Supabase** (PostgreSQL with built-in auth)
- **Railway**
- **PlanetScale**
- **AWS RDS**
- **Google Cloud SQL**

## 4. Prisma Setup

### Initialize Prisma

```bash
# Generate Prisma client
pnpm prisma generate

# Run database migrations
pnpm prisma db push

# (Optional) Seed the database
pnpm prisma db seed
```

### Prisma Commands Reference

```bash
# Generate Prisma client after schema changes
pnpm prisma generate

# Push schema changes to database (development)
pnpm prisma db push

# Create and run migrations (production)
pnpm prisma migrate dev --name init

# View database in Prisma Studio
pnpm prisma studio

# Reset database (⚠️ This will delete all data)
pnpm prisma migrate reset
```

## 5. Authentication Setup

The project uses **NextAuth.js** with credentials provider and Prisma adapter.

### Generate NextAuth Secret

```bash
# Generate a secure secret
openssl rand -base64 32
```

Add this to your `.env.local` as `NEXTAUTH_SECRET`.

### Authentication Features Included:

- ✅ User registration with email/password
- ✅ Login/logout functionality
- ✅ Session management
- ✅ Protected routes
- ✅ User profile management

## 6. Development Server

Start the development server:

```bash
# Using pnpm (recommended)
pnpm dev

# Or using npm
npm run dev
```

The application will be available at `http://localhost:3000`.

## 7. Project Structure

```
ui-v2/
├── src/
│   ├── app/                    # Next.js 13+ App Router
│   │   ├── api/               # API routes
│   │   ├── auth/              # Authentication pages
│   │   ├── dashboard/         # Dashboard pages
│   │   ├── create-test/       # Test creation workflow
│   │   └── layout.tsx         # Root layout
│   ├── components/            # React components
│   │   ├── ui/               # Shadcn/ui components
│   │   ├── workflow/         # Workflow-specific components
│   │   └── providers/        # Context providers
│   ├── lib/                   # Utility libraries
│   │   ├── auth/             # Authentication configuration
│   │   └── prisma.ts         # Prisma client
│   ├── schemas/              # Zod validation schemas
│   └── generated/            # Generated Prisma client
├── prisma/
│   └── schema.prisma         # Database schema
├── public/                   # Static assets
└── package.json             # Dependencies and scripts
```

## 8. Key Features and Technologies

### Frontend Stack:
- **Next.js 15.5.3** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Shadcn/ui** - UI component library
- **React Hook Form** - Form management
- **Zod** - Schema validation
- **Lucide React** - Icons

### Backend Stack:
- **NextAuth.js** - Authentication
- **Prisma** - Database ORM
- **PostgreSQL** - Database
- **API Routes** - Backend endpoints

### Development Tools:
- **ESLint** - Code linting
- **TypeScript** - Type checking
- **Turbopack** - Build tool (Next.js)

## 9. Available Scripts

```json
{
  "dev": "next dev --turbopack",           // Start development server
  "build": "next build --turbopack",      // Build for production
  "start": "next start",                  // Start production server
  "lint": "eslint"                        // Run ESLint
}
```

## 10. Database Schema Overview

The project includes these main models:

- **User** - User accounts and authentication
- **Account** - OAuth account linking
- **Session** - User sessions
- **TestWorkflow** - Test creation workflows
- **VerificationToken** - Email verification

## 11. Workflow Features

### Test Creation Workflow:
1. **Step 1: User Story** - Define test requirements
2. **Step 2: Processing** - AI processing of requirements
3. **Step 3: Plan Output** - Test plan generation with versioning
4. **Step 4: Test Script** - Final test script generation

### Key Components:
- `UserStoryStepWithRHF` - Form-based user story input
- `ProcessingStep` - AI processing visualization
- `PlanOutputStep` - Interactive test plan with accordion UI
- `TestScriptStep` - Final script generation and download

## 12. Troubleshooting

### Common Issues:

1. **Database Connection Errors**:
   ```bash
   # Check if PostgreSQL is running
   pg_isready -d e2e_ai_db
   
   # Verify DATABASE_URL format
   echo $DATABASE_URL
   ```

2. **Prisma Issues**:
   ```bash
   # Clear Prisma cache
   rm -rf node_modules/.prisma
   pnpm prisma generate
   ```

3. **Build Errors**:
   ```bash
   # Clear Next.js cache
   rm -rf .next
   pnpm run build
   ```

4. **TypeScript Errors**:
   ```bash
   # Restart TypeScript language server in VS Code
   # Ctrl+Shift+P -> "TypeScript: Restart TS Server"
   ```

### Environment Issues:

- Ensure all environment variables are set correctly
- Check that DATABASE_URL points to an accessible database
- Verify NEXTAUTH_SECRET is at least 32 characters

## 13. Production Deployment

### Build for Production:

```bash
# Build the application
pnpm run build

# Start production server
pnpm start
```

### Environment Variables for Production:

```env
NODE_ENV=production
DATABASE_URL="your-production-database-url"
NEXTAUTH_URL="https://your-domain.com"
NEXTAUTH_SECRET="your-production-secret"
```

### Database Migrations:

```bash
# Run migrations in production
pnpm prisma migrate deploy
```

## 14. VS Code Setup (Recommended)

Install these VS Code extensions for the best development experience:

```json
{
  "recommendations": [
    "bradlc.vscode-tailwindcss",
    "ms-vscode.vscode-typescript-next",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-eslint",
    "prisma.prisma"
  ]
}
```

### VS Code Settings:

Create `.vscode/settings.json`:

```json
{
  "typescript.preferences.includePackageJsonAutoImports": "on",
  "typescript.suggest.autoImports": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.formatOnSave": true,
  "tailwindCSS.includeLanguages": {
    "typescript": "javascript",
    "typescriptreact": "javascript"
  }
}
```

## 15. Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Stage changes
git add .

# Commit changes
git commit -m "feat: your feature description"

# Push to remote
git push origin feature/your-feature-name
```

## 16. Testing

### Manual Testing Checklist:

- [ ] User registration works
- [ ] User login/logout works
- [ ] Dashboard loads correctly
- [ ] Test workflow navigation works
- [ ] All workflow steps function properly
- [ ] Database operations work
- [ ] Forms validate correctly

### Automated Testing (Future):

The project is set up to support:
- Jest for unit testing
- Cypress/Playwright for E2E testing
- React Testing Library for component testing

## Support

If you encounter any issues during setup:

1. Check this documentation first
2. Review the project's GitHub issues
3. Check the Next.js and Prisma documentation
4. Contact the development team

---

**Last Updated**: October 1, 2025  
**Version**: 1.0.0  
**Maintainer**: E2E AI Development Team
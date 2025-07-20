# Deployment Guide for Lekzy-TTP SMS Sender

## Required Environment Variables for Deployment

Before deploying, ensure these environment variables are set in your deployment configuration:

### Essential Variables:
- `SECRET_KEY` - Flask session security key
- `ADMIN_PASSWORD` - Admin panel password  
- `DEFAULT_API_KEY` - Default API key for the system
- `DATABASE_URL` - PostgreSQL connection string (usually auto-set by Replit)

### Optional Variables:
- `FLASK_DEBUG` - Set to "false" for production (default: false)
- `PORT` - Application port (default: 5000)
- `HOST` - Application host (default: 0.0.0.0)

## Deployment Steps:

1. **Set Environment Variables:**
   In your Replit deployment settings, add:
   ```
   SECRET_KEY=your-secret-key-here
   ADMIN_PASSWORD=your-admin-password
   DEFAULT_API_KEY=your-default-api-key
   ```

2. **Deployment Command Options (use in this order):**
   1. **RECOMMENDED**: `python server.py`
   2. Alternative: `python app.py`
   3. Alternative: `python main.py` 
   4. Backup: `python run.py`
   5. WSGI: `gunicorn server:application --bind 0.0.0.0:$PORT`

3. **Health Check Endpoints:**
   - Main health check: `/health`
   - Detailed status: `/status`
   - Main app: `/`

## Troubleshooting Deployment Blocks:

### Issue: "Application not responding on port 5000"
**Solution:** The app is configured to run on port 5000. Check deployment logs.

### Issue: "Health check failing"
**Solution:** Test endpoints:
- `curl https://your-app.replit.app/health`
- `curl https://your-app.replit.app/status`

### Issue: "Environment variables missing"
**Solution:** Add all required variables to deployment configuration.

### Issue: "Database connection failed"
**Solution:** Ensure PostgreSQL is enabled in your Replit project.

## Files Created for Deployment:
- `run.py` - Main entry point
- `wsgi.py` - WSGI server compatibility
- `Procfile` - Process definition
- `runtime.txt` - Python version specification

## Contact Support:
If deployment continues to fail, contact Replit support with:
1. Deployment error message
2. Project URL
3. This deployment guide
# CmdMate Terminal - Troubleshooting Guide

## 🚨 Common Deployment Issues

### Health Check Failures

**Problem**: Service unavailable, health check failed
```
Attempt #1 failed with service unavailable. Continuing to retry for 1m37s
1/1 replicas never became healthy!
Healthcheck failed!
```

**Solutions**:

1. **Check Health Endpoint**:
   ```bash
   curl http://your-app-url/health
   ```
   Should return: `{"status": "healthy", "service": "CmdMate Terminal", "version": "1.0.0"}`

2. **Verify Port Configuration**:
   - Ensure your app binds to `0.0.0.0` and uses `$PORT` environment variable
   - Check that the port is correctly exposed

3. **Check Application Logs**:
   ```bash
   # Railway
   railway logs
   
   # Heroku
   heroku logs --tail
   
   # Docker
   docker logs <container_id>
   ```

### Port Issues

**Problem**: Port already in use or binding issues

**Solutions**:
1. **Kill existing processes**:
   ```bash
   # Windows
   netstat -ano | findstr :5000
   taskkill /PID <PID> /F
   
   # Linux/macOS
   lsof -ti:5000 | xargs kill -9
   ```

2. **Use different port**:
   ```bash
   PORT=8080 python main.py --web
   ```

### Dependencies Issues

**Problem**: Module not found errors

**Solutions**:
1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Check Python version**:
   ```bash
   python --version  # Should be 3.7+
   ```

3. **Virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   pip install -r requirements.txt
   ```

### Memory Issues

**Problem**: Out of memory errors

**Solutions**:
1. **Reduce workers** (for Gunicorn):
   ```bash
   gunicorn --workers 1 --bind 0.0.0.0:$PORT wsgi:app
   ```

2. **Increase container memory**:
   - Railway: Upgrade to higher tier
   - Heroku: Use Performance dynos
   - Docker: Increase memory limits

### Timeout Issues

**Problem**: Request timeouts

**Solutions**:
1. **Increase timeout**:
   ```bash
   gunicorn --timeout 120 --bind 0.0.0.0:$PORT wsgi:app
   ```

2. **Check long-running commands**:
   - Avoid commands that run indefinitely
   - Use timeouts for subprocess calls

## 🔧 Platform-Specific Fixes

### Railway

1. **Environment Variables**:
   ```bash
   railway variables set PORT=5000
   railway variables set FLASK_ENV=production
   ```

2. **Redeploy**:
   ```bash
   railway redeploy
   ```

### Heroku

1. **Check buildpacks**:
   ```bash
   heroku buildpacks
   heroku buildpacks:set heroku/python
   ```

2. **Scale dynos**:
   ```bash
   heroku ps:scale web=1
   ```

3. **View logs**:
   ```bash
   heroku logs --tail
   ```

### Docker

1. **Build with no cache**:
   ```bash
   docker build --no-cache -t cmdmate .
   ```

2. **Run with proper port mapping**:
   ```bash
   docker run -p 5000:5000 cmdmate
   ```

3. **Check container health**:
   ```bash
   docker ps
   docker inspect <container_id> | grep Health
   ```

## 🐛 Debugging Steps

### 1. Local Testing
```bash
# Test health endpoint
python -c "import requests; print(requests.get('http://localhost:5000/health').json())"

# Test web interface
python main.py --web
# Open http://localhost:5000
```

### 2. Check Logs
```bash
# Enable debug mode
export FLASK_DEBUG=1
python main.py --web
```

### 3. Test Commands
```bash
# Test basic functionality
python -c "from terminal import Terminal; t = Terminal(); print(t.execute_command('help'))"
```

### 4. Network Testing
```bash
# Test if port is accessible
telnet localhost 5000
curl -I http://localhost:5000
```

## 🚀 Quick Fixes

### Immediate Solutions

1. **Restart the service**:
   ```bash
   # Railway
   railway redeploy
   
   # Heroku
   heroku restart
   
   # Docker
   docker restart <container_id>
   ```

2. **Check environment**:
   ```bash
   echo $PORT
   echo $FLASK_ENV
   ```

3. **Verify files**:
   ```bash
   ls -la
   cat requirements.txt
   cat Procfile
   ```

### Emergency Fallback

If all else fails, use the simple start command:

```bash
# For Railway/Heroku
python main.py --web

# For Docker
CMD ["python", "main.py", "--web"]
```

## 📞 Getting Help

1. **Check logs first** - Most issues are visible in logs
2. **Test locally** - Ensure it works on your machine
3. **Check platform documentation** - Railway, Heroku, Docker docs
4. **Verify environment variables** - PORT, FLASK_ENV, etc.

## ✅ Success Indicators

Your deployment is working when you see:

1. **Health check returns 200**:
   ```json
   {"status": "healthy", "service": "CmdMate Terminal", "version": "1.0.0"}
   ```

2. **Web interface loads**:
   - Terminal interface appears
   - Commands execute successfully
   - Real-time monitoring works

3. **No error logs**:
   - Clean startup logs
   - No timeout errors
   - No memory issues

## 🔄 Redeployment

After fixing issues:

1. **Commit changes**:
   ```bash
   git add .
   git commit -m "Fix deployment issues"
   git push origin main
   ```

2. **Redeploy**:
   ```bash
   # Railway
   railway redeploy
   
   # Heroku
   git push heroku main
   
   # Docker
   docker build -t cmdmate .
   docker run -p 5000:5000 cmdmate
   ```

Your CmdMate Terminal should now deploy successfully! 🎉

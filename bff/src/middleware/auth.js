const { CognitoJwtVerifier } = require('aws-jwt-verify');

// Initialize Cognito JWT Verifier
const verifier = CognitoJwtVerifier.create({
  userPoolId: process.env.COGNITO_USER_POOL_ID || 'us-east-1_dummyPool',
  tokenUse: 'access',
  clientId: process.env.COGNITO_CLIENT_ID || 'dummyClientId',
});

const verifyCognitoToken = async (req, res, next) => {
  const authHeader = req.headers.authorization;

  // Allow unauthenticated access in local development if header is omitted
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    console.warn('[BFF Auth] No Bearer token provided. Proceeding as unauthenticated.');
    return next();
  }

  const token = authHeader.split(' ')[1];

  try {
    const payload = await verifier.verify(token);
    
    // Attach validated payload to request object
    req.user = payload;
    
    // Inject headers to forward identity to microservices
    req.headers['x-user-id'] = payload.sub;
    req.headers['x-user-role'] = payload['cognito:groups'] ? payload['cognito:groups'][0] : 'Customer';

    console.log(`[BFF Auth] Verified Cognito User: ${payload.sub}`);
    next();
  } catch (err) {
    console.error('[BFF Auth] Invalid Token:', err.message);
    return res.status(401).json({ error: 'Unauthorized: Invalid or expired Cognito token' });
  }
};

module.exports = { verifyCognitoToken };
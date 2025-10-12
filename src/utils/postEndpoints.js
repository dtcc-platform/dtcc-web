const LOGIN_SUFFIX_RE = /\/login\/?$/i

const ENV = {
  VITE_POST_AUTH_URL: import.meta.env.VITE_POST_AUTH_URL,
  VITE_POST_PUBLISH_URL: import.meta.env.VITE_POST_PUBLISH_URL,
  VITE_CHAT_AUTH_URL: import.meta.env.VITE_CHAT_AUTH_URL,
  VITE_CHAT_PUBLISH_URL: import.meta.env.VITE_CHAT_PUBLISH_URL,
}

function sanitizeEndpoint(value) {
  if (typeof value !== 'string') {
    return ''
  }
  const trimmed = value.trim()
  return trimmed || ''
}

function pickEnvValue(...keys) {
  for (const key of keys) {
    const raw = sanitizeEndpoint(ENV[key])
    if (raw) {
      return raw
    }
  }
  return ''
}

function derivePublishFromAuth(authEndpoint) {
  const base = sanitizeEndpoint(authEndpoint)
  if (!base) return ''
  try {
    const url = new URL(base)
    if (!LOGIN_SUFFIX_RE.test(url.pathname)) {
      return ''
    }
    url.pathname = url.pathname.replace(LOGIN_SUFFIX_RE, '/post')
    return url.toString()
  } catch {
    return ''
  }
}

export function resolvePostEndpoints() {
  const authEndpoint = pickEnvValue('VITE_POST_AUTH_URL', 'VITE_CHAT_AUTH_URL')
  const explicitPublish = pickEnvValue('VITE_POST_PUBLISH_URL', 'VITE_CHAT_PUBLISH_URL')

  let publishEndpoint = explicitPublish
  let publishDerivedFromAuth = false
  let publishMisconfigured = false

  if (!publishEndpoint) {
    const inferred = derivePublishFromAuth(authEndpoint)
    if (inferred) {
      publishEndpoint = inferred
      publishDerivedFromAuth = true
    }
  } else if (authEndpoint && publishEndpoint === authEndpoint) {
    const inferred = derivePublishFromAuth(authEndpoint)
    if (inferred) {
      publishEndpoint = inferred
      publishDerivedFromAuth = true
    } else {
      publishEndpoint = ''
      publishMisconfigured = true
    }
  }

  return {
    authEndpoint,
    publishEndpoint,
    publishDerivedFromAuth,
    publishWasExplicit: Boolean(explicitPublish),
    publishMisconfigured,
  }
}

// Use the operating system's resolver for local SMTP. Some Windows networks
// block the DNS packets sent by Node's c-ares resolver even though system DNS
// works. Keep the original hostname for TLS certificate verification.
const dns = require('node:dns')
const path = require('node:path')
const { createRequire } = require('node:module')
const host = process.env.PULSE_SMTP_HOST

if (host) {
  const localRequire = createRequire(path.join(__dirname, '..', '.runtime', 'n8n', 'node_modules', 'n8n-nodes-base', 'package.json'))
  const shared = localRequire('nodemailer/lib/shared')
  const original = shared.resolveHostname
  shared.resolveHostname = (options, callback) => {
    if (!options || options.host !== host) return original(options, callback)
    dns.lookup(host, { family: 4, all: true }, (error, entries) => {
      if (error) return callback(error)
      const addresses = entries.map(entry => entry.address)
      callback(null, { host: addresses[0], servername: options.servername || host, _addresses: addresses, cached: false })
    })
  }
}

exports.config = {
    user: 'TLCS',
    password: 'trafficlight',
    server: 'Eddys-Laptop\\SQLEXPRESS',
    database: 'TLCS',
    pool: {
        max: 10,
        min: 0,
        idleTimeoutMillis: 30000
    },
    options: {
        instanceName: 'SQLEXPRESS',
        enableArithAbort: true,
        trustServerCertificate: true
    }
}
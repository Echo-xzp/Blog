const fs = require('fs')

const replace_config = () =>{
    const configData = fs.readFileSync('_config.butterfly.yml', 'utf8')
    
    const token = process.env.GITALK_TOKEN
    if (token !== undefined && token.length > 0) {
        console.log('替换TOKEN中......')
        configData.replace('{GITALK_TOKEN}',token)
        fs.writeFileSync('_config.butterfly.yml', configData, 'utf8')
    }
}

module.exports = {
    replace_config,
}
const fs = require('fs')

const replace_config = () =>{
    let configData = fs.readFileSync('_config.butterfly.yml', 'utf8')
    
    const token = process.env.GITALK_TOKEN
    if (token !== undefined && token.length > 0) {
        console.log('替换TOKEN中......')
        configData = configData.replace(/{GITALK_TOKEN}/g,token)
        fs.writeFileSync('_config.butterfly.yml', configData, 'utf8')
        console.log('替换TOKEN完成')
    }
}

module.exports = {
    replace_config,
}
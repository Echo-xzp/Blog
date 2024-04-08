const fs = require('fs');
const yaml = require('js-yaml');

const update_config = () =>{
    try {
        // 读取Hexo配置文件
        const configData = fs.readFileSync('_config.butterfly.yml', 'utf8');
        
        // 解析YAML数据
        const parsedConfig = yaml.load(configData);
    
        // 修改你想要的变量，例如修改title
        parsedConfig.gitalk.client_secret = process.env.GITALK_TOKEN;
    
        // 将修改后的配置转换回YAML格式
        const newYaml = yaml.dump(parsedConfig);
    
        // 将修改后的配置写回配置文件中
        fs.writeFileSync('_config.butterfly.yml', newYaml, 'utf8');
    
        console.log("Hexo配置文件已修改成功！");
    } catch (err) {
        console.error('修改Hexo配置文件时出现错误:', err);
    }
}

module.exports = {
    update_config,
}
Instructions:

​	-u 网站地址

​	-p 代理地址

​	-f https需设置为-f 1

​	-t 指定js文件请求超时时间（适用于js文件过大时）

​	-m 新增 webpack 打包模式适配，默认值为0，代表常规chunk模式



[关于网站地址]

​	工具默认生成的BaseURL遵循以下规则：

  1. 如果-u的参数（即网站地址）以/结尾，默认会将整个网站地址作为BaseURL进行拼接访问。

     ​	-如http://example.com/web/, 即整个工具均以http://example.com/web/为BaseURL

  2. 如果-u的参数（即网站地址）以某个详细的路径或文件作为结尾，则默认去除最后一项路径及参数，生成BaseURL。

     ​	-如http://example.com/user/login, 即以http://example.com/user/作为BaseURL

     ​	-如http://example.com/file/a.jsp?id=1, 即以http://example.com/file/作为BaseURL

     ​	-如http://example.com/project/dept/query, 即以http://example.com/project/dept/作为BaseURL



[关于JS路径错误的人工干预]

​	目前对于JS路径的错误收集存在两种校验方式：

1. 均返回404的错误码：此时表示超过5%的JS文件请求无法访问，提示【当前页面关联js超过5%页面不存在，是否进行baseURL手动调整(Y/N):】，用户输入y后填写BaseURL进行二次尝试。
1. 均重定向至首页或跳转第三方页面：此时表示超过10%的JS文件长度为一致的，极有可能均重定向至固定页面，提示【当前页面关联js超过5%文件长度一致，是否进行baseURL手动调整(Y/N):】，用户输入y后填写BaseURL进行二次尝试。

注意：在工具目录中存在tmp文件夹，该文件夹下以【随机六位字符_网站地址_result.txt】的格式存储了从主站点中提取的webpack打包JS文件名，如不确定其是否携带js/一类的前缀，请查看后再填写BaseURL。

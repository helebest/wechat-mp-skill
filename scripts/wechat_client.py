#!/usr/bin/env python3
"""
微信公众号 API 客户端
处理认证、请求和 access_token 管理
"""

import os
import time
import json
import requests
from typing import Optional, Dict, Any, BinaryIO
from pathlib import Path
from dotenv import load_dotenv, find_dotenv


class WeChatAPIError(Exception):
    """微信 API 错误"""
    def __init__(self, errcode: int, errmsg: str):
        self.errcode = errcode
        self.errmsg = errmsg
        super().__init__(f"[{errcode}] {errmsg}")


class WeChatClient:
    """微信公众号 API 客户端"""
    
    BASE_URL = "https://api.weixin.qq.com"
    TOKEN_CACHE_FILE = ".wechat_token_cache.json"
    
    def __init__(
        self,
        appid: Optional[str] = None,
        appsecret: Optional[str] = None,
        token_cache_dir: Optional[str] = None,
        env_file: Optional[str] = None
    ):
        """
        初始化客户端
        
        Args:
            appid: 公众号 AppID，默认从环境变量 WECHAT_APPID 读取
            appsecret: 公众号 AppSecret，默认从环境变量 WECHAT_APPSECRET 读取
            token_cache_dir: token 缓存目录，默认当前目录
            env_file: .env 文件路径，默认自动查找
        """
        # 自动加载 .env 文件（从当前目录向上查找）
        load_dotenv(env_file or find_dotenv(usecwd=True))
        
        self.appid = appid or os.environ.get("WECHAT_APPID")
        self.appsecret = appsecret or os.environ.get("WECHAT_APPSECRET")
        
        if not self.appid or not self.appsecret:
            raise ValueError(
                "请设置 WECHAT_APPID 和 WECHAT_APPSECRET 环境变量，"
                "或创建 .env 文件，或在初始化时传入 appid 和 appsecret 参数"
            )
        
        self.token_cache_dir = Path(token_cache_dir or ".")
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0
        
        # 尝试从缓存加载 token
        self._load_token_cache()
    
    def _get_cache_path(self) -> Path:
        """获取 token 缓存文件路径"""
        return self.token_cache_dir / self.TOKEN_CACHE_FILE
    
    def _load_token_cache(self) -> None:
        """从缓存加载 token"""
        cache_path = self._get_cache_path()
        if cache_path.exists():
            try:
                with open(cache_path, "r") as f:
                    cache = json.load(f)
                    if cache.get("appid") == self.appid:
                        self._access_token = cache.get("access_token")
                        self._token_expires_at = cache.get("expires_at", 0)
            except (json.JSONDecodeError, IOError):
                pass
    
    def _save_token_cache(self) -> None:
        """保存 token 到缓存"""
        cache_path = self._get_cache_path()
        try:
            with open(cache_path, "w") as f:
                json.dump({
                    "appid": self.appid,
                    "access_token": self._access_token,
                    "expires_at": self._token_expires_at
                }, f)
        except IOError:
            pass
    
    def _is_token_valid(self) -> bool:
        """检查 token 是否有效（预留 5 分钟缓冲）"""
        return (
            self._access_token is not None 
            and time.time() < self._token_expires_at - 300
        )
    
    def get_access_token(self, force_refresh: bool = False) -> str:
        """
        获取 access_token
        
        Args:
            force_refresh: 是否强制刷新
            
        Returns:
            access_token 字符串
        """
        if not force_refresh and self._is_token_valid():
            return self._access_token
        
        url = f"{self.BASE_URL}/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.appid,
            "secret": self.appsecret
        }
        
        resp = requests.get(url, params=params)
        result = resp.json()
        
        if "errcode" in result and result["errcode"] != 0:
            raise WeChatAPIError(result["errcode"], result.get("errmsg", ""))
        
        self._access_token = result["access_token"]
        self._token_expires_at = time.time() + result.get("expires_in", 7200)
        self._save_token_cache()
        
        return self._access_token
    
    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        auto_retry: bool = True
    ) -> Dict[str, Any]:
        """
        发送 API 请求
        
        Args:
            method: HTTP 方法 (GET/POST)
            endpoint: API 端点（如 /cgi-bin/material/add_material）
            params: URL 参数
            json_data: JSON 请求体
            files: 上传文件
            data: form-data
            auto_retry: token 过期时是否自动重试
            
        Returns:
            API 响应 JSON
        """
        url = f"{self.BASE_URL}{endpoint}"

        # 添加 access_token
        params = params or {}
        params["access_token"] = self.get_access_token()

        # 处理 JSON 数据，确保中文不被转义
        headers = {}
        if json_data is not None:
            data = json.dumps(json_data, ensure_ascii=False).encode('utf-8')
            headers['Content-Type'] = 'application/json'

        # 发送请求
        resp = requests.request(
            method=method,
            url=url,
            params=params,
            headers=headers if headers else None,
            files=files,
            data=data
        )
        
        # 处理响应
        result = resp.json()
        
        # 检查错误
        errcode = result.get("errcode", 0)
        if errcode != 0:
            # token 过期，自动重试
            if errcode in (40001, 40014, 42001) and auto_retry:
                self.get_access_token(force_refresh=True)
                return self.request(
                    method, endpoint, params, json_data, files, data,
                    auto_retry=False
                )
            raise WeChatAPIError(errcode, result.get("errmsg", ""))
        
        return result
    
    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """GET 请求"""
        return self.request("GET", endpoint, params=params)
    
    def post(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """POST 请求"""
        return self.request(
            "POST", endpoint, 
            json_data=json_data, files=files, data=data
        )
    
    def upload_file(
        self,
        endpoint: str,
        file_path: str,
        file_field: str = "media",
        extra_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        上传文件
        
        Args:
            endpoint: API 端点
            file_path: 文件路径
            file_field: 文件字段名
            extra_data: 额外的 form 数据
        """
        with open(file_path, "rb") as f:
            files = {file_field: (Path(file_path).name, f)}
            return self.post(endpoint, files=files, data=extra_data)
    
    def download_file(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        下载文件
        
        Returns:
            文件二进制内容
        """
        url = f"{self.BASE_URL}{endpoint}"
        params = params or {}
        params["access_token"] = self.get_access_token()
        
        if json_data:
            resp = requests.post(url, params=params, json=json_data)
        else:
            resp = requests.get(url, params=params)
        
        # 检查是否是 JSON 错误响应
        content_type = resp.headers.get("Content-Type", "")
        if "application/json" in content_type or "text/plain" in content_type:
            try:
                result = resp.json()
                if "errcode" in result and result["errcode"] != 0:
                    raise WeChatAPIError(result["errcode"], result.get("errmsg", ""))
            except json.JSONDecodeError:
                pass
        
        return resp.content


# 便捷函数
def create_client(
    appid: Optional[str] = None,
    appsecret: Optional[str] = None
) -> WeChatClient:
    """创建微信客户端实例"""
    return WeChatClient(appid=appid, appsecret=appsecret)


if __name__ == "__main__":
    # 测试
    client = WeChatClient()
    token = client.get_access_token()
    print(f"Access Token: {token[:20]}...")

import json, glob, os, base64 
from urllib.parse import quote 

def make_hy2_link(cfg: dict, fallback_name: str) -> str:
    name = cfg.get("remarks") or fallback_name 

     # Ищем outbound с tag=proxy (или первый не direct/block) 
     outbounds = cfg.get("outbounds", []) 
     proxy = next((o for o in outbounds if o.get("tag") == "proxy"), None) 
     if proxy is None: 
         proxy = next((o for o in outbounds if o.get("protocol") not in ("freedom", "blackhole")), None) 
    if proxy is None: 
             raise ValueError("No proxy outbound found") 

         # ВАШ случай: protocol=hysteria + version=2 => hysteria2 link 
        
         if proxy.get("protocol") != "hysteria": 
            raise ValueError(f"Unsupported protocol for this repo demo: {proxy.get('protocol')}") 
         
         settings = proxy.get("settings", {}) or {}
         stream = proxy.get("streamSettings", {}) or {}
         hy = stream.get("hysteriaSettings", {}) or {} 
         tls = stream.get("tlsSettings", {}) or {} 
         
         addr = settings.get("address") 
         port = settings.get("port")
         auth = hy.get("auth")
         
         sni = tls.get("serverName") or addr fp = tls.get("fingerprint") 
         alpn_list = tls.get("alpn") or []
         alpn = alpn_list[0] if alpn_list else None 
         
         if not (addr and port and auth): 
            raise ValueError("Missing address/port/auth in config")
         
        params = [] 
            if sni: params.append(f"sni={sni}") 
            if alpn: params.append(f"alpn={alpn}") 
            if fp: params.append(f"fp={fp}") qs = ("?" + "&".join(params)) if params else ""
     
         return f"hysteria2://{auth}@{addr}:{port}/{qs}#{quote(name, safe='')}"
     
    lines = [] 
    for path in sorted(glob.glob("configs/*.json")): 
        with open(path, "r", encoding="utf-8") as f: 
            cfg = json.load(f)
            
            fallback = os.path.splitext(os.path.basename(path))[0] 
            lines.append(make_hy2_link(cfg, fallback)) 
            
            sub_text = "\n".join(lines) + ("\n" if lines else "") 
            
            with open("sub.txt", "w", encoding="utf-8") as f: f.write(sub_text) 
            
            # Опционально: base64-подписка (если какой-то клиент требует именно base64) 
        
            b64 = base64.b64encode(sub_text.encode("utf-8")).decode("ascii") 
            with open("sub_base64.txt", "w", encoding="utf-8") as f: 
                f.write(b64)
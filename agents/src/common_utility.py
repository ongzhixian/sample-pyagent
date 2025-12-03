import json
import os

def get_secret(secret_key_id:str) -> str | None :
    sec_file_path = os.path.join(
        os.environ['APPDATA'],
        "Microsoft",
        "UserSecrets",
        "kairos",
        "pyagent-secrets.json")
    with open(sec_file_path, 'r', encoding='utf-8-sig') as data_file:
        data = json.load(data_file)
        if secret_key_id in data:
            return data[secret_key_id]
    return None

def main():
    print("Sec: {0}".format(get_secret('AzureOpenAiApiKey')))
    print("Sec: {0}".format(get_secret('Xxx')))

if __name__ == "__main__":
    main()
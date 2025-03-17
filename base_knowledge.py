import json
from pymilvus import connections, Collection, utility
from pymilvus import CollectionSchema, FieldSchema, DataType
import numpy as np
import pickle
import os
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.hunyuan.v20230901 import hunyuan_client, models

class BaseVectorizer:
    """基础向量化工具"""
    def __init__(self, secret_id, secret_key):
        try:
            self.cred = credential.Credential(secret_id, secret_key)
            http_profile = HttpProfile()
            http_profile.endpoint = "hunyuan.tencentcloudapi.com"
            
            client_profile = ClientProfile()
            client_profile.httpProfile = http_profile
            
            self.client = hunyuan_client.HunyuanClient(
                self.cred, 
                "ap-guangzhou",
                client_profile
            )
            
        except Exception as e:
            print(f"初始化向量化工具失败: {e}")
            raise e

    def get_vector(self, text):
        """获取文本向量"""
        try:
            req = models.GetEmbeddingRequest()
            params = {
                "Input": text,
                "Model": "bge-large-zh-v1.5"
            }
            req.from_json_string(json.dumps(params))
            
            response = self.client.GetEmbedding(req)
            
            if hasattr(response, 'Data') and response.Data:
                embedding_data = response.Data[0]
                if hasattr(embedding_data, 'Embedding'):
                    return embedding_data.Embedding
            
            return None
        except Exception as e:
            print(f"向量化失败: {e}")
            return None

class BaseKnowledgeBase:
    """基础知识库"""
    def __init__(self, collection_name, vector_dim=1024):
        self.collection_name = collection_name
        self.vector_dim = vector_dim
        self.vectors_cache = {}
        self.cache_file = f"vectors_cache_{collection_name}.pkl"
        
        # 加载缓存
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'rb') as f:
                    self.vectors_cache = pickle.load(f)
                print(f"已加载{len(self.vectors_cache)}个向量缓存")
            except Exception as e:
                print(f"加载缓存失败: {e}")
        
        try:
            # 连接到 Milvus
            connections.connect(
                alias="default",
                host="localhost",
                port="19530"
            )
            
            # 检查并创建集合
            if not utility.has_collection(collection_name):
                self._create_collection()
            else:
                self.collection = Collection(collection_name)
            
            # 加载集合
            self.collection.load()
            
        except Exception as e:
            print(f"初始化知识库失败: {e}")
            raise e

    def _create_collection(self):
        """创建新的集合"""
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=1048),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=self.vector_dim),
            FieldSchema(name="type", dtype=DataType.VARCHAR, max_length=64)
        ]
        schema = CollectionSchema(fields=fields, description="知识库")
        self.collection = Collection(name=self.collection_name, schema=schema)
        
        index_params = {
            "metric_type": "IP",
            "index_type": "IVF_FLAT",
            "params": {"nlist": self.vector_dim}
        }
        self.collection.create_index(field_name="vector", index_params=index_params)

    def save_cache(self):
        """保存向量缓存"""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.vectors_cache, f)
        except Exception as e:
            print(f"保存缓存失败: {e}")

    def add_knowledge(self, content, content_type, vector):
        """添加知识"""
        try:
            vector_np = np.array(vector, dtype=np.float32)
            if len(vector_np.shape) == 1:
                vector_np = vector_np.reshape(1, -1)
            
            data = [
                [content],
                vector_np,
                [content_type]
            ]
            
            self.collection.insert(data)
            return True
        except Exception as e:
            print(f"添加知识失败: {e}")
            return False

    def search(self, query_vector, limit=5):
        """搜索知识"""
        try:
            results = self.collection.search(
                data=[query_vector],
                anns_field="vector",
                param={"metric_type": "IP", "params": {"nprobe": 10}},
                limit=limit,
                output_fields=["text", "type"]
            )
            
            return [{
                "text": hit.entity.get('text'),
                "type": hit.entity.get('type'),
                "distance": hit.distance
            } for hits in results for hit in hits]
            
        except Exception as e:
            print(f"搜索失败: {e}")
            return []

    def cleanup(self):
        """清理资源"""
        try:
            if hasattr(self, 'collection'):
                self.collection.release()
            connections.disconnect("default")
            self.save_cache()
        except Exception as e:
            print(f"清理资源失败: {e}") 
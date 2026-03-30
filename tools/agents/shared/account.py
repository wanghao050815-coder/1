"""账号管理系统 - 多账号隔离和权限控制

基于真实数据驱动的多账号系统，支持主子关系和权限模型。
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional
import json
from datetime import datetime


class AccountType(Enum):
    """账号类型"""
    MASTER = "master"          # 主账号，完整控制权
    SUB = "sub"                # 子账号，受权限限制
    STANDALONE = "standalone"  # 独立账号


class PermissionLevel(Enum):
    """权限级别"""
    FULL = "full"              # 完整：文案生成、发布、数据分析、管理
    PUBLISH = "publish"        # 发布权：仅可发布文案，不可分析
    READ_ONLY = "read_only"    # 只读：仅可查看数据


@dataclass
class Account:
    """账号对象 - 多账号系统的核心单位"""
    account_id: str                     # 账号唯一ID (B1, B2, B3...)
    account_name: str                   # 账号显示名称
    type: AccountType                   # 账号类型
    permission_level: PermissionLevel   # 权限级别

    # 关系字段
    master_account: Optional[str] = None    # 主账号ID（若为子账号）
    sub_accounts: list = field(default_factory=list)  # 子账号列表

    # 平台绑定
    platforms: dict = field(default_factory=dict)  # {platform: account_name}

    # 元数据
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "account_id": self.account_id,
            "account_name": self.account_name,
            "type": self.type.value,
            "permission_level": self.permission_level.value,
            "master_account": self.master_account,
            "sub_accounts": self.sub_accounts,
            "platforms": self.platforms,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
        }


class AccountManager:
    """账号配置和权限管理"""

    def __init__(self, data_root: Path):
        self.data_root = Path(data_root)
        self.accounts_dir = self.data_root / "accounts"
        self.config_file = self.accounts_dir / "account.json"
        self._accounts_cache = None

    def load_accounts(self) -> dict[str, Account]:
        """加载所有账号配置"""
        if not self.config_file.exists():
            return {}

        try:
            with open(self.config_file, encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

        accounts = {}
        for acc_id, acc_data in data.get("accounts", {}).items():
            try:
                accounts[acc_id] = Account(
                    account_id=acc_id,
                    account_name=acc_data.get("name", acc_id),
                    type=AccountType(acc_data.get("type", "standalone")),
                    permission_level=PermissionLevel(acc_data.get("permission", "full")),
                    master_account=acc_data.get("master"),
                    sub_accounts=acc_data.get("subs", []),
                    platforms=acc_data.get("platforms", {}),
                    created_at=acc_data.get("created_at"),
                    updated_at=acc_data.get("updated_at"),
                    metadata=acc_data.get("metadata", {}),
                )
            except ValueError as e:
                print(f"警告：账号 {acc_id} 配置错误：{e}")
                continue

        return accounts

    def get_account(self, account_id: str) -> Optional[Account]:
        """获取单个账号"""
        accounts = self.load_accounts()
        return accounts.get(account_id)

    def has_permission(self, account_id: str, action: str) -> bool:
        """检查账号是否有权限执行某操作

        Args:
            account_id: 账号ID
            action: 操作类型 (copywrite, publish, analytics, delete, manage)

        Returns:
            True 如果有权限，False 否则
        """
        account = self.get_account(account_id)
        if not account:
            return False

        # 权限矩阵：权限级别 -> 允许的操作列表
        permission_matrix = {
            "full": ["copywrite", "publish", "analytics", "delete", "manage"],
            "publish": ["publish"],
            "read_only": ["view_analytics"],
        }

        allowed_actions = permission_matrix.get(account.permission_level.value, [])
        return action in allowed_actions

    def get_account_hierarchy(self, account_id: str) -> dict:
        """获取账号的层级关系（主账号 + 所有子账号）

        Args:
            account_id: 账号ID

        Returns:
            {
                "master": Account | None,
                "self": Account,
                "subs": [Account, ...]
            }
        """
        account = self.get_account(account_id)
        if not account:
            return {}

        hierarchy = {"self": account}

        # 获取主账号（如果当前是子账号）
        if account.master_account:
            master = self.get_account(account.master_account)
            hierarchy["master"] = master

        # 获取所有子账号
        subs = []
        for sub_id in account.sub_accounts:
            sub = self.get_account(sub_id)
            if sub:
                subs.append(sub)
        hierarchy["subs"] = subs

        return hierarchy

    def list_all_accounts(self) -> list[Account]:
        """列出所有账号"""
        accounts = self.load_accounts()
        return list(accounts.values())

    def create_account(self, account_id: str, account_name: str,
                      account_type: str = "standalone",
                      permission: str = "full",
                      master: Optional[str] = None,
                      platforms: Optional[dict] = None) -> Account:
        """创建新账号

        Args:
            account_id: 账号ID (B1, B2, ...)
            account_name: 账号显示名称
            account_type: 账号类型 (master/sub/standalone)
            permission: 权限级别 (full/publish/read_only)
            master: 主账号ID（若为子账号）
            platforms: 平台绑定 {platform: account_name}

        Returns:
            新创建的 Account 对象
        """
        now = datetime.now().isoformat()

        account = Account(
            account_id=account_id,
            account_name=account_name,
            type=AccountType(account_type),
            permission_level=PermissionLevel(permission),
            master_account=master,
            platforms=platforms or {},
            created_at=now,
            updated_at=now,
        )

        # 更新配置文件
        self._save_account(account)

        # 如果是子账号，更新主账号的 sub_accounts 列表
        if master:
            master_account = self.get_account(master)
            if master_account and account_id not in master_account.sub_accounts:
                master_account.sub_accounts.append(account_id)
                self._save_account(master_account)

        return account

    def _save_account(self, account: Account):
        """保存账号配置到文件"""
        self.accounts_dir.mkdir(parents=True, exist_ok=True)

        # 加载现有配置
        if self.config_file.exists():
            with open(self.config_file, encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {"metadata": {}, "accounts": {}}

        # 更新或新增账号
        data["accounts"][account.account_id] = account.to_dict()
        data["metadata"]["updated_at"] = datetime.now().isoformat()

        # 保存到文件
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def initialize_default_accounts(data_root: Path) -> None:
    """初始化默认账号配置

    创建 B1（主）、B2（子）、B3（子）三个默认账号
    """
    manager = AccountManager(data_root)

    # 检查是否已存在
    if manager.get_account("B1"):
        return  # 已初始化

    # 创建 B1 主账号
    manager.create_account(
        account_id="B1",
        account_name="邪健仙主号",
        account_type="master",
        permission="full",
        platforms={"douyin": "邪健仙", "xiaohongshu": "邪健仙official", "bilibili": "邪健仙"}
    )

    # 创建 B2 子账号
    manager.create_account(
        account_id="B2",
        account_name="邪修宗男团号",
        account_type="sub",
        permission="publish",
        master="B1",
        platforms={"douyin": "邪修宗男团"}
    )

    # 创建 B3 子账号
    manager.create_account(
        account_id="B3",
        account_name="邪修宗女团号",
        account_type="sub",
        permission="publish",
        master="B1",
        platforms={"douyin": "邪修宗女团"}
    )

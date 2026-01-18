"""
配置差异对比引擎
"""
import difflib
import logging

logger = logging.getLogger(__name__)


class DiffEngine:
    """配置差异对比引擎"""
    
    @staticmethod
    def _filter_dynamic_lines(lines):
        """
        过滤掉动态内容行（时间戳、版本信息等）
        
        Args:
            lines: 配置行列表
            
        Returns:
            过滤后的行列表
        """
        filtered = []
        # 需要过滤的模式（可根据实际情况调整）
        skip_patterns = [
            'clock',  # 时钟信息
            'ntp clock-period',  # NTP时钟
            '!Time:',  # 时间戳
            '!Last configuration change',  # 最后配置变更时间
            '!NVRAM config last updated',  # NVRAM更新时间
            'version ',  # 版本信息（可选，如果需要跟踪版本变化则保留）
        ]
        
        for line in lines:
            line_lower = line.lower().strip()
            # 跳过空行和注释行（以!开头）
            if not line_lower or line_lower.startswith('!'):
                # 但保留重要的注释行
                if any(pattern in line_lower for pattern in ['!last', '!nvram']):
                    continue
                filtered.append(line)
                continue
            
            # 检查是否匹配需要跳过的模式
            should_skip = False
            for pattern in skip_patterns:
                if pattern in line_lower:
                    should_skip = True
                    break
            
            if not should_skip:
                filtered.append(line)
        
        return filtered
    
    @classmethod
    def compare_configs(cls, old_config, new_config):
        """
        对比两个配置的差异
        
        Args:
            old_config: 旧配置内容
            new_config: 新配置内容
            
        Returns:
            差异结果字典
        """
        # 标准化配置内容（去除首尾空白）
        old_config = old_config.strip()
        new_config = new_config.strip()
        
        if old_config == new_config:
            return {
                'has_changes': False,
                'diff': '',
                'added_lines': 0,
                'removed_lines': 0,
                'modified_lines': 0
            }
        
        # 分割为行
        old_lines = old_config.splitlines(keepends=True)
        new_lines = new_config.splitlines(keepends=True)
        
        # 过滤动态内容行
        old_filtered = cls._filter_dynamic_lines(old_lines)
        new_filtered = cls._filter_dynamic_lines(new_lines)
        
        # 再次比较过滤后的内容
        old_filtered_text = ''.join(old_filtered).strip()
        new_filtered_text = ''.join(new_filtered).strip()
        
        if old_filtered_text == new_filtered_text:
            logger.debug("配置内容相同（过滤动态内容后）")
            return {
                'has_changes': False,
                'diff': '',
                'added_lines': 0,
                'removed_lines': 0,
                'modified_lines': 0
            }
        
        # 使用difflib进行对比（使用过滤后的内容）
        diff = difflib.unified_diff(
            old_filtered,
            new_filtered,
            fromfile='old_config',
            tofile='new_config',
            lineterm='',
            n=3  # 上下文行数
        )
        
        diff_text = ''.join(diff)
        
        # 统计变更行数
        diff_lines = diff_text.splitlines()
        added_lines = sum(1 for line in diff_lines if line.startswith('+') and not line.startswith('+++'))
        removed_lines = sum(1 for line in diff_lines if line.startswith('-') and not line.startswith('---'))
        
        # 如果diff为空，说明没有实际变更
        if not diff_text.strip():
            return {
                'has_changes': False,
                'diff': '',
                'added_lines': 0,
                'removed_lines': 0,
                'modified_lines': 0
            }
        
        logger.info(f"配置差异: 新增 {added_lines} 行, 删除 {removed_lines} 行")
        
        return {
            'has_changes': True,
            'diff': diff_text,
            'added_lines': added_lines,
            'removed_lines': removed_lines,
            'modified_lines': 0  # 统一diff中修改显示为删除+添加
        }
    
    @staticmethod
    def has_changes(diff_result):
        """
        判断是否有变更
        
        Args:
            diff_result: compare_configs返回的结果
            
        Returns:
            bool
        """
        return diff_result.get('has_changes', False)
    
    @staticmethod
    def format_diff(diff_result, html=False):
        """
        格式化差异输出
        
        Args:
            diff_result: compare_configs返回的结果
            html: 是否返回HTML格式
            
        Returns:
            格式化后的差异文本
        """
        if not diff_result['has_changes']:
            return "配置无变更"
        
        if html:
            # HTML格式的差异显示
            diff_lines = diff_result['diff'].splitlines()
            html_diff = []
            for line in diff_lines:
                if line.startswith('+++') or line.startswith('---'):
                    html_diff.append(f'<div class="diff-header">{line}</div>')
                elif line.startswith('@@'):
                    html_diff.append(f'<div class="diff-hunk">{line}</div>')
                elif line.startswith('+'):
                    html_diff.append(f'<div class="diff-added">{line}</div>')
                elif line.startswith('-'):
                    html_diff.append(f'<div class="diff-removed">{line}</div>')
                else:
                    html_diff.append(f'<div class="diff-context">{line}</div>')
            return '\n'.join(html_diff)
        else:
            return diff_result['diff']
    
    @staticmethod
    def get_summary(diff_result):
        """
        获取差异摘要
        
        Args:
            diff_result: compare_configs返回的结果
            
        Returns:
            摘要字符串
        """
        if not diff_result['has_changes']:
            return "配置无变更"
        
        return f"新增 {diff_result['added_lines']} 行, 删除 {diff_result['removed_lines']} 行"


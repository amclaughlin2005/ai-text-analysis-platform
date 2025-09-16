"""
Text Validation Service for cleaning legal industry terms and law firm names
Provides intelligent filtering for word cloud generation
"""

import re
import logging
from typing import List, Set, Dict, Any
from collections import Counter

logger = logging.getLogger(__name__)

class TextValidationService:
    """Service for validating and cleaning text content before analysis"""
    
    # Industry-specific terms to always remove
    INDUSTRY_BLACKLIST = {
        'singletonschriber', 'com', 'docwebviewer', 'filevine', 'filevineapp',
        'docviewer', 'view', 'source', 'embedding', 'page', 'https', 'http',
        'www', 'app', 'portal', 'clientportal', 'casemanager', 'clientaccess',
        'project', 'custom', 'details', 'item', 'see', 'link', 'click', 'here'
    }
    
    # Common legal technology terms
    LEGAL_TECH_TERMS = {
        'filevine', 'lexisnexis', 'westlaw', 'clio', 'mycase', 'practicemaster',
        'amicus', 'timesolv', 'abacuslaw', 'smokeball', 'lawpay', 'confidesk',
        'centrestack', 'netdocuments', 'imanage', 'worldox', 'pclaw',
        'timeslips', 'billing', 'invoicing', 'docketing'
    }
    
    # Common file/document references
    DOCUMENT_TERMS = {
        'pdf', 'doc', 'docx', 'xlsx', 'ppt', 'pptx', 'jpg', 'jpeg', 'png',
        'gif', 'tiff', 'bmp', 'zip', 'rar', 'tar', 'gz', 'html', 'htm',
        'xml', 'json', 'csv', 'txt', 'rtf'
    }
    
    # URL/Email patterns
    URL_PATTERN = re.compile(r'https?://[^\s]+|www\.[^\s]+')
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    
    # Law firm name patterns (common suffixes)
    LAW_FIRM_SUFFIXES = {
        'law', 'llc', 'pllc', 'pc', 'inc', 'corp', 'corporation', 'ltd', 'limited',
        'group', 'firm', 'associates', 'partners', 'partnership', 'office', 'offices',
        'legal', 'attorney', 'attorneys', 'counsel', 'counselors', 'solicitors',
        'barristers', 'advocates', 'esquire', 'esq'
    }
    
    @classmethod
    def clean_text_for_analysis(
        cls, 
        text: str, 
        tenant_info: Dict[str, Any] = None,
        additional_blacklist: List[str] = None
    ) -> str:
        """
        Clean text content by removing industry terms, law firm names, and noise
        
        Args:
            text: The text to clean
            tenant_info: Tenant information to help identify law firm names
            additional_blacklist: Additional terms to remove
            
        Returns:
            Cleaned text ready for word cloud analysis
        """
        if not text:
            return ""
        
        # Convert to lowercase for processing
        cleaned_text = text.lower()
        
        # Remove URLs and email addresses
        cleaned_text = cls.URL_PATTERN.sub(' ', cleaned_text)
        cleaned_text = cls.EMAIL_PATTERN.sub(' ', cleaned_text)
        
        # Build comprehensive blacklist
        blacklist = cls._build_blacklist(tenant_info, additional_blacklist)
        
        # Remove blacklisted terms
        words = cleaned_text.split()
        filtered_words = []
        
        for word in words:
            # Clean word of punctuation
            clean_word = re.sub(r'[^\w]', '', word)
            
            # Skip if empty, too short, or blacklisted
            if (len(clean_word) < 2 or 
                clean_word in blacklist or
                cls._is_law_firm_term(clean_word, tenant_info) or
                cls._is_noise_term(clean_word)):
                continue
                
            filtered_words.append(clean_word)
        
        return ' '.join(filtered_words)
    
    @classmethod
    def _build_blacklist(
        cls, 
        tenant_info: Dict[str, Any] = None,
        additional_blacklist: List[str] = None
    ) -> Set[str]:
        """Build comprehensive blacklist of terms to remove"""
        blacklist = set()
        
        # Add industry terms
        blacklist.update(cls.INDUSTRY_BLACKLIST)
        blacklist.update(cls.LEGAL_TECH_TERMS)
        blacklist.update(cls.DOCUMENT_TERMS)
        blacklist.update(cls.LAW_FIRM_SUFFIXES)
        
        # Add tenant-specific terms
        if tenant_info:
            # Extract words from tenant/org names
            for field in ['tenant_name', 'org_name', 'organization', 'company']:
                if field in tenant_info and tenant_info[field]:
                    tenant_words = cls._extract_significant_words(str(tenant_info[field]))
                    blacklist.update(tenant_words)
        
        # Add additional blacklist terms
        if additional_blacklist:
            blacklist.update(word.lower() for word in additional_blacklist)
        
        # Add common stop words
        blacklist.update(cls._get_stop_words())
        
        return blacklist
    
    @classmethod
    def _extract_significant_words(cls, text: str) -> List[str]:
        """Extract significant words from law firm names (avoiding common words)"""
        if not text:
            return []
        
        words = re.findall(r'\w+', text.lower())
        significant_words = []
        
        # Skip very common words but keep firm-specific terms
        skip_words = {'the', 'and', 'of', 'for', 'group', 'law', 'llc', 'pllc', 'pc'}
        
        for word in words:
            if len(word) > 2 and word not in skip_words:
                significant_words.append(word)
        
        return significant_words
    
    @classmethod
    def _is_law_firm_term(cls, word: str, tenant_info: Dict[str, Any] = None) -> bool:
        """Check if word appears to be part of a law firm name"""
        if not word or len(word) < 3:
            return False
        
        # Check against known suffixes
        if word in cls.LAW_FIRM_SUFFIXES:
            return True
        
        # Check if word appears in tenant information
        if tenant_info:
            tenant_text = ' '.join(str(v) for v in tenant_info.values() if v)
            if word in tenant_text.lower():
                return True
        
        # Pattern matching for law firm-like terms
        law_patterns = [
            r'.*law.*',
            r'.*legal.*',
            r'.*attorney.*',
            r'.*counsel.*',
            r'.*firm.*'
        ]
        
        for pattern in law_patterns:
            if re.match(pattern, word):
                return True
        
        return False
    
    @classmethod
    def _is_noise_term(cls, word: str) -> bool:
        """Check if word is likely noise (numbers, short words, etc.)"""
        if not word or len(word) < 2:
            return True
        
        # Skip pure numbers
        if word.isdigit():
            return True
        
        # Skip mixed alphanumeric that's mostly numbers
        if len(re.sub(r'\d', '', word)) < len(word) * 0.3:
            return True
        
        # Skip very short words
        if len(word) < 3:
            return True
        
        return False
    
    @classmethod
    def _get_stop_words(cls) -> Set[str]:
        """Get comprehensive stop words list"""
        return {
            # Common English stop words
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been', 
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 
            'us', 'them', 'my', 'your', 'his', 'our', 'their',
            
            # Legal document stop words
            'plaintiff', 'defendant', 'versus', 'vs', 'case', 'matter', 'file',
            'document', 'page', 'section', 'paragraph', 'line', 'exhibit',
            'attachment', 'appendix', 'schedule', 'addendum',
            
            # Time/date words
            'january', 'february', 'march', 'april', 'may', 'june', 'july',
            'august', 'september', 'october', 'november', 'december',
            'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
            'am', 'pm', 'today', 'yesterday', 'tomorrow', 'week', 'month', 'year',
            
            # Common verbs/actions that aren't meaningful
            'said', 'says', 'see', 'show', 'shows', 'go', 'goes', 'come', 'comes',
            'get', 'gets', 'got', 'put', 'puts', 'take', 'takes', 'took', 'give',
            'gives', 'gave', 'make', 'makes', 'made'
        }
    
    @classmethod
    def extract_tenant_info_from_data(cls, data_record: Dict[str, Any]) -> Dict[str, Any]:
        """Extract tenant information from a data record for filtering"""
        tenant_info = {}
        
        # Common tenant field names
        tenant_fields = [
            'tenant_name', 'tenant_id', 'shard_name', 'org_name', 'orgname',
            'organization', 'company', 'firm', 'client'
        ]
        
        for field in tenant_fields:
            if field in data_record and data_record[field]:
                tenant_info[field] = data_record[field]
        
        return tenant_info
    
    @classmethod
    def validate_word_list(
        cls,
        words: List[Dict[str, Any]],
        tenant_info: Dict[str, Any] = None,
        additional_blacklist: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Validate and filter a list of word cloud words
        
        Args:
            words: List of word dictionaries with 'word', 'frequency', etc.
            tenant_info: Tenant information for filtering
            additional_blacklist: Additional terms to remove
            
        Returns:
            Filtered list of words
        """
        if not words:
            return []
        
        blacklist = cls._build_blacklist(tenant_info, additional_blacklist)
        filtered_words = []
        
        for word_data in words:
            word = word_data.get('word', '').lower().strip()
            
            # Skip if blacklisted or noise
            if (not word or 
                word in blacklist or
                cls._is_law_firm_term(word, tenant_info) or
                cls._is_noise_term(word)):
                continue
            
            # Keep the word
            filtered_words.append(word_data)
        
        logger.info(f"🧹 Filtered {len(words) - len(filtered_words)} words, kept {len(filtered_words)}")
        return filtered_words

'''
Created on Apr 19, 2012

@package: superdesk media archive
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for meta type.
'''

from .domain_archive import modelArchive
from ally.api.config import service, call
from ally.api.type import Iter

# --------------------------------------------------------------------

@modelArchive(id='Key')
class MetaType:
    '''
    Provides the meta types.
    '''
    Key = str # Provides the key that represents the meta type
    Name = str

# --------------------------------------------------------------------

@service
class IMetaTypeService:
    '''
    Provides the meta type services.
    '''

    @call
    def getByKey(self, key:MetaType.Key) -> MetaType:
        '''
        Provides the meta type based on the key.
        '''

    @call
    def getMetaTypes(self, offset:int=None, limit:int=None) -> Iter(MetaType):
        '''
        Provides the meta type's.
        '''

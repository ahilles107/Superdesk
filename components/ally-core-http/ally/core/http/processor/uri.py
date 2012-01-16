'''
Created on Jun 28, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides the URI request path handler.
'''

from ally.container.ioc import injected
from ally.core.http.spec import RequestHTTP
from ally.core.spec.codes import RESOURCE_NOT_FOUND, RESOURCE_FOUND
from ally.core.spec.resources import ConverterPath, Path, ResourcesManager
from ally.core.spec.server import Response, Processor, ProcessorsChain, \
    EncoderPath
from urllib.parse import urlencode, urlparse, urlunsplit, parse_qsl
import logging

# --------------------------------------------------------------------

log = logging.getLogger(__name__)

# --------------------------------------------------------------------

@injected
class URIHandler(Processor):
    '''
    Implementation for a processor that provides the searches based on the request URL the resource path, also
    populates the parameters and extension format on the request.
    
    Provides on request: resourcePath, params, accContentTypes
    Provides on response: code, encoderPath
    
    Requires on request: path
    Requires on response: NA
    '''

    resourcesManager = ResourcesManager
    # The resources manager that will provide the path to the resource node.
    converterPath = ConverterPath
    # The converter path used for handling the URL path.
    scheme = 'http'
    # The scheme of the uri
    headerHost = 'Host'
    # The header in which the host is provided.

    def __init__(self):
        assert isinstance(self.resourcesManager, ResourcesManager), \
        'Invalid resources manager %s' % self.resourcesManager
        assert isinstance(self.converterPath, ConverterPath), 'Invalid ConverterPath object %s' % self.converterPath
        assert isinstance(self.scheme, str), 'Invalid string %s' % self.scheme
        assert isinstance(self.headerHost, str), 'Invalid string %s' % self.headerHost

    def process(self, req, rsp, chain):
        '''
        @see: Processor.process
        '''
        assert isinstance(req, RequestHTTP), 'Invalid HTTP request %s' % req
        assert isinstance(rsp, Response), 'Invalid response %s' % rsp
        assert isinstance(chain, ProcessorsChain), 'Invalid processors chain %s' % chain
        if isinstance(req.path, str):
            url = urlparse(req.path)
            paths = url.path.split('/')
            req.params.extend(parse_qsl(url.query, True, False))
        else:
            paths = list(req.path)

        i = paths[-1].rfind('.') if len(paths) > 0 else -1
        if i < 0:
            extension = None
        else:
            extension = paths[-1][i + 1:].lower()
            paths[-1] = paths[-1][0:i]
        paths = [p for p in paths if p]

        rsp.encoderPath = EncoderPathURI(req.headers.pop(self.headerHost, ''), self, req.rootURI, extension)
        if extension:
            rsp.contentType = extension
            req.accContentTypes.insert(0, extension)

        resourcePath = self.resourcesManager.findResourcePath(self.converterPath, paths)
        assert isinstance(resourcePath, Path)
        if not resourcePath.node:
            # we stop the chain processing
            rsp.setCode(RESOURCE_NOT_FOUND, 'Cannot find resources for path')
            return
        rsp.code = RESOURCE_FOUND
        req.resourcePath = resourcePath
        assert log.debug('Successfully found resource for path %s with extension %s', req.path, extension) or True
        chain.process(req, rsp)

# --------------------------------------------------------------------

class EncoderPathURI(EncoderPath):
    '''
    Provides encoding for the URI paths generated by the URI processor.
    '''

    def __init__(self, host, uri, rootURI, ext):
        '''
        @param host: string
            The host string.
        @param uri: URI
            The URI processor of the encoder path.
        @param rootURI: string | None
            The root URI to be considered for constructing a request path, basically the relative path root. None if the path
            is not relative.
        @param ext: string
            The extension to use on the encoded paths.
        '''
        assert not host or isinstance(host, str), 'Invalid host %s' % host
        assert isinstance(uri, URIHandler), 'Invalid URI handler %s' % uri
        assert not rootURI or isinstance(rootURI, str), 'Invalid root URI %s' % rootURI
        assert not ext or isinstance(ext, str), 'Invalid extension %s' % ext
        self._host = host
        self._uri = uri
        self._rootURI = rootURI
        self._ext = ext

    def encode(self, path, parameters = None):
        '''
        @see: EncoderPath.encode
        '''
        assert isinstance(path, Path), 'Invalid path %s' % path
        uri = self._uri
        assert isinstance(uri, URIHandler)
        paths = path.toPaths(uri.converterPath)
        if self._ext: paths.append('.' + self._ext)
        elif path.node.isGroup: paths.append('')
        query = urlencode(parameters) if parameters else ''
        return urlunsplit((uri.scheme, self._host, self._rootURI + '/'.join(paths), query, ''))

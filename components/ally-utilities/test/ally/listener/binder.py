'''
Created on Aug 24, 2011

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides unit testing for the binder module.
'''

from ally.container.proxy import createProxy, ProxyWrapper
from ally.listener.binder import bindLock, clearBindings
import unittest

# --------------------------------------------------------------------

class A:
    
    def methodLocked(self, test, lock, count=1, exc=False):
        assert isinstance(test, TestBinder)
        assert isinstance(lock, Lock)
        test.assertTrue(lock.count == count)
        if exc: raise KeyError('Some exception')
        
    def methodNotLocked(self, test, lock):
        assert isinstance(test, TestBinder)
        assert isinstance(lock, Lock)
        test.assertTrue(lock.count == 0)

class Lock:
    
    def __init__(self):
        self.count = 0
    
    def acquire(self): self.count += 1
    
    def release(self): self.count -= 1

# --------------------------------------------------------------------

class TestBinder(unittest.TestCase):
        
    def testBindLock(self):
        AProxy = createProxy(A)
        
        proxy = AProxy(ProxyWrapper(A()))
        
        assert isinstance(proxy, A)
        
        lock = Lock()
        bindLock(proxy.methodLocked, lock)
        
        proxy.methodLocked(self, lock)
        self.assertTrue(lock.count == 0)
        
        self.assertRaises(KeyError, proxy.methodLocked, self, lock, exc=True)
        self.assertTrue(lock.count == 0)
        
        proxy.methodNotLocked(self, lock)
        self.assertTrue(lock.count == 0)
        
        clearBindings(proxy.methodLocked)
        proxy.methodLocked(self, lock, count=0)
        self.assertTrue(lock.count == 0)
        
# --------------------------------------------------------------------
  
if __name__ == '__main__':
    unittest.main()


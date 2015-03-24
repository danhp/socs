from __future__ import division # consider all division as floating point division
from HelperClasses import Material
from Ray import Ray, IntersectionResult
import GeomTransform as GT
import numpy as np
import math

 # use this for testing if a variable is close to 0, a variable x is close to 0
# if |x| < EPS_DISTANCE or in the code:
# np.fabs(x) < EPS_DISTANCE
EPS_DISTANCE = 1e-9

class Sphere:
  """

  Sphere class

  Properties that a sphere has are center, radius and material.
  The intersection method returns the result of ray-sphere intersection.
  
  """
   
  def __init__(self, params = {}):
      #radius = 1.0, center = [0.0, 0.0, 0.0], material = Material()):
      self.material = params.get('material', Material())
      self.radius = float(params.get('radius', 1.0))
      self.center = np.array(params.get('center', [0., 0., 0.]))
  
  def intersect(self, ray):
      ''' 
      input: ray in the same coordinate system as the sphere
      output: IntersectionResult, contains the intersection point, normal,
              distance from the eye position and material (see Ray.py)
      Let, the ray be P = P0 + tv, where P0 = eye, v = ray direction
      We want to find t.
      sphere with center Pc and radius r:
      (P - Pc)^T (P - Pc) = r^2      
      We need to consider the different situations that can arise with ray-sphere
      intersection.
      NOTE 1: If the eye position is inside the sphere it SHOULD return the 
      ray-sphere intersection along the view direction. Because the point *is
      visible* to the eye as far as ray-sphere intersection is concerned. 
      The color used for rendering that point will be considered during the 
      lighting and shading stage. In general there's no reason why there can't
      be a viewer and light sources inside a sphere.
      NOTE 2: If the ray origin is on the surface of the sphere then the nearest
      intersection should be ignored otherwise we'll have problems where
      the surface point cannot 'see' the light because of self intersection.
      '''
      ''' 
      Implement intersection between the ray and the current object and 
      return IntersectionResult variable (isect) which will store the 
      intersection point, the normal at the intersection and material of the 
      object at the intersection point.
      '''
      isect = IntersectionResult() # by default isect corresponds to no intersection
      
      global EPS_DISTANCE # use this for testing if a variable is close to 0
      #TODO ===== BEGIN SOLUTION HERE =====

      # ===== END SOLUTION HERE =====
      return isect


class Plane:
  """

  Plane class

  Plane passing through origin with a given normal. If the second material is
  defined, it has a checkerboard pattern.
  
  A plane can be used as a floor, wall or ceiling. E.g. see cornell.xml 

  """

  def __init__(self, params = {}):
      #normal=[0.0,1.0,0.0], material = Material(), material2 = 0 ):
      self.normal = GT.normalize(np.array(params.get('normal', [0.0,1.0,0.0])))
      material_list = params.get('material', [Material(), None])
      if type(material_list) is not list:
          self.material = material_list
          self.material2 = None
      else:
          self.material = material_list[0]
          self.material2 = material_list[1]
      #print(params)
      #print(self.normal, self.material, self.material2)
    
  def intersect(self, ray):
    ''' 
    Find the intersection of the ray with the plane. Consider the ray and the
    plane to be in the same coordinate system. Return the result of intersection
    in a variable of type IntersectionResult.
    
    Note: 
    1. For checkerboard planes there are two materials. You need to consider 
    what the material is at the intersection point. If the plane has only 1
    material then self.material2 is set to None. To determine whether the plane
    has checkerboard pattern, you should have code like:
    if self.material2 is not None:
        # the plane has checkerboard pattern
    2. If a ray originates on the plane and goes away from the plane then that
    is not considered as an intersection. Otherwise we'll have problem with 
    shadow rays.
    3. If the ray lies entirely on the plane we don't consider that to be an
    intersection (i.e. we won't see the plane in the rendered scene.)
    see TestXZPlaneThroughOriginNoIntersectionWithRay.test_ray_on_plane in 
    TestPlaneIntersection.py for corresponding test case.
    '''
    
    ''' 
    Implement intersection between the ray and the current object and 
    return IntersectionResult variable (isect) which will store the 
    intersection point, the normal at the intersection and material of the 
    object at the intersection point. For checkerboard planes you need to 
    decide which of the two materials to use at the intersection point.
    '''
    isect = IntersectionResult()

    global EPS_DISTANCE # use this for testing if a variable is close to 0
    #TODO ===== BEGIN SOLUTION HERE =====  

    # ===== END SOLUTION HERE ===== 
    return isect
    
class Box:
  """

  Box class

  Axis-aligned box defined by setting a pair of opposing points.

  """

  def __init__(self, params = {}):
      #minPoint = [-1, -1, -1], maxPoint = [1, 1, 1], material = Material()):
      self.minPoint = np.array(params.get('min', [-1., -1., -1.]))
      self.maxPoint = np.array(params.get('max', [1., 1., 1.]))
      self.material = params.get('material', Material())
      assert(np.all(self.minPoint <= self.maxPoint))
      #print(self.minPoint, self.maxPoint, self.material)
      
  def intersect(self, ray):
    """
      The box can be viewed as the intersection of 6 planes. The following code
      checks the intersection to all planes and the order.  Depending on the
      order we detect the intersection.
      
      Note: 
      1. At the box corners you can return any one of the three normals.
      2. You can assume that all rays originate outside the box 
      3. A ray can originate on one of the plane or corners of the box and go
         outside in which case we do not consider that to be an intersection
         with the box.
    """
    ''' 
    Implement intersection between the ray and the current object and 
    return IntersectionResult variable (isect) which will store the 
    intersection point, the normal at the intersection and material of the 
    object at the intersection point.
    '''
    isect = IntersectionResult()
    
    global EPS_DISTANCE # use this for testing if a variable is close to 0
    # tmin and tmax are temporary variables to keep track of the order of the
    # plane intersections.  The ray will pass through at least a set of parallel
    # planes. tmin is the last intersection of the first planes of each set, and
    # tmax is the first intersection of the last planes of each set. 
    tmax = np.inf
    tmin = -np.inf
    
    #TODO ===== BEGIN SOLUTION HERE =====

    # ===== END SOLUTION HERE =====
    return isect
    
class SceneNode:
  """
  
  SceneNode class
  
  This intersectable object is used as a transformation in the scene creation.
  It allows the scene to be build in a hierarchical fashion. It allows rotations
  and translations.  The intersection ray will be transformed to find the intersection
  in the transformed space, and the intersection result is transformed back to
  the original coordinate space.  It performs a test for all its children.
  
  """
  def __init__(self, M = np.eye(4), params = None):
    self.children = []
    self.M = M
    if params is not None:
        rot_angles = np.array(params.get('rotation', [0., 0., 0.]))
        translate_amount = np.array(params.get('translation', [0., 0., 0.]))
        scale_amount = np.array(params.get('scale', [1., 1., 1.]))
        # compute the transformation matrix that gets applied to all children of this node
        Tform = GT.translate(translate_amount) *  GT.rotateX(rot_angles[0]) * \
            GT.rotateY(rot_angles[1]) * GT.rotateZ(rot_angles[2]) * \
            GT.scale(scale_amount)
        self.M = Tform.getA()
        
    self.Minv = np.linalg.inv(self.M)
    #print(self.M, self.Minv)
    
  def intersect(self, ray):
    ''' 
    Implement intersection between the ray and the current object and 
    return IntersectionResult variable (isect) which will store the 
    intersection point, the normal at the intersection and material of the 
    object at the intersection point. The variable isect should contain the
    nearest intersection point and all its properties.
    '''
    isect = IntersectionResult()
    
    global EPS_DISTANCE # use this for testing if a variable is close to 0  
    #TODO ===== BEGIN SOLUTION HERE =====

    # ===== END SOLUTION HERE =====
    return isect  
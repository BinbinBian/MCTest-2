import theano
import theano.tensor as T
import numpy as np
import random
from itertools import izip
from theano.compile.debugmode import DebugMode

import func as F

class RNN_net:
    def __init__(self , layers , Ws = None , Whs = None , bs = None , batch_size = 1 ,
                    momentum_type = "None" , act_type = "ReLU" , cost_type = "CE"  ):
        #test parameter define ( should be inputs later.)
        self.layers        = layers
        self.batch_size    = batch_size

        l_rate             = T.scalar(dtype='float32') # np.float32(0.0001)
        init               = np.float32(0.1)
        rms_alpha          = T.scalar(dtype='float32') # np.float32(0.9)
        clip_range         = T.scalar(dtype='float32')
        momentum           = T.scalar(dtype='float32')
       # validation.
        if Ws is not None and bs is not None and Whs is not None:
            assert len(layers) == len(Ws) and len(layers) == len(bs) and len(layers) == len(Whs)

       # train input
        x_seq = T.tensor3(dtype='float32')
        y_hat = T.tensor3(dtype='float32')
        mask  = T.tensor3(dtype='float32')

       # train parameter initialization
        self.W  =  [ None ]
        self.Wh =  [ None ]
        self.b  =  [ None ]

        a_seq = [ x_seq ]
        ls    = [ None ]

        for idx in range( len(self.layers)-1 ):
            # init b , Wh , W
            #self.b.append ( theano.shared(np.asarray (np.random.uniform(-init , init , size = ( self.layers[idx+1] )) , 'float32')))
            self.b.append ( theano.shared(np.asarray ( np.zeros( self.layers[idx+1] ) , 'float32')) )
            self.Wh.append (theano.shared(np.asarray ( np.cast['float32'](0.1)*np.identity(self.layers[idx+1]), 'float32')) )
            self.W.append(theano.shared(np.asarray ( np.random.uniform(-init , init , size = ( self.layers[idx] , self.layers[idx+1] )), 'float32'  )  ))
            # import the  model from outside
            if Ws is not None:
                self.W[idx+1].set_value( Ws[idx+1].get_value() )
            if bs is not None:
                self.b[idx+1].set_value( bs[idx+1].get_value() )
            if Whs is not None:
                self.Wh[idx+1].set_value( Whs[idx+1].get_value() )

            # declaration a RNN layer
            if idx==0 : #means it's the first layer
                temp_layers = RNN_first_layer(self.W[idx+1] , self.Wh[idx+1] , self.b[idx+1] , self.layers[idx+1] , a_seq[idx] , self.batch_size  , act_type)
            elif idx == len(self.layers)-2: # Last Layer
                temp_layers = RNN_last_layer(self.W[idx+1]  , self.b[idx+1] , a_seq[idx] )
            else:
                temp_layers = RNN_layers(self.W[idx+1] , self.Wh[idx+1] , self.b[idx+1] , self.layers[idx+1] , a_seq[idx] , self.batch_size  , act_type)

            ls.append(temp_layers)
            # output the 'a' of RNN layers
            a_seq.append(temp_layers.layer_out)
       
       # define parameters 
        parameters = self.W[1:] + self.Wh[1:-1] + self.b[1:] 
 
       # define what are outputs.
        y_seq = a_seq[-1]
        y_out = y_seq * T.addbroadcast( mask , 2  )

       # define cost
        if(cost_type == "CE"):
            y_out_a = F.softmax(y_out)
        else:
            y_out_a = F.softmax(y_out)
        cost = F.cost_func( y_out_a , y_hat , cost_type )
       # compute gradient

        gradients = T.grad(cost , parameters )
        gradient = [ ]
        for idx in range(len(gradients)):
            gradient.append(T.clip(gradients[idx] , -clip_range , clip_range) )
        #
        pre_parameters = []
        for param in parameters:
            pre_parameters.append( theano.shared(
                np.asarray(
                    np.zeros(param.get_value().shape) , 'float32' )
            ))
        # for rmsprop
        sq_sum_grad = []
        for param in parameters:
            sq_sum_grad.append( theano.shared(
                np.asarray(
                    np.zeros(param.get_value().shape) , 'float32' )
            ))
        # for NAG
        pre_update = []
        for param in parameters:
            pre_update.append( theano.shared(
                np.asarray(
                    np.zeros(param.get_value().shape) , 'float32' )
            ))

        def update(parameters , gradients ):
            if momentum_type == "rmsprop":
                parameter_updates = [ (p, p - l_rate * g / T.sqrt(ssg) )
                    if ssg.get_value().sum() != 0 else (p, p-l_rate*g) \
                    for p,g,ssg in izip(parameters,gradient,sq_sum_grad) ]
                parameter_updates += [ (ssg, rms_alpha*ssg + (np.cast['float32'](1.0)-rms_alpha)*(g**2)  ) \
                           for g , ssg in izip( gradient , sq_sum_grad) ]
                return parameter_updates
            elif momentum_type == "NAG":
                parameter_updates = [ ( pre_p , pre_p + momentum*v - l_rate*g )\
                    for pre_p , g , v in izip(pre_parameters, gradient, pre_update) ]
                parameter_updates += [ ( p , pre_p + 2*( momentum*v - l_rate*g ) ) \
                    for p , pre_p , g , v in izip(parameters, pre_parameters, gradient, pre_update) ]
                parameter_updates += [ ( v , -l_rate*g + momentum*v )\
                    for g , v in izip(gradient , pre_update) ]
                return parameter_updates
            elif momentum_type == "rms+NAG":
                parameter_updates =  [ ( pre_p , pre_p + momentum*v - l_rate*g/T.sqrt(ssg) ) \
                    if ssg.get_value().sum() != 0 else (pre_p , pre_p - l_rate*g + momentum*v ) \
                    for pre_p , g , v , ssg in izip(pre_parameters, gradient, pre_update,sq_sum_grad) ]
                parameter_updates += [ ( p , pre_p + 2*( momentum*v - l_rate*g/T.sqrt(ssg) ) ) \
                    if ssg.get_value().sum() != 0 else ( p , pre_p + 2*( -l_rate*g + momentum*v) ) \
                    for p , pre_p , g , v ,ssg in izip(parameters, pre_parameters, gradient, pre_update , sq_sum_grad) ]
                parameter_updates += [ ( v , -l_rate*g/T.sqrt(ssg) + momentum*v )\
                    if ssg.get_value().sum() != 0 else ( v  , - l_rate*g + momentum*v ) \
                    for g , v , ssg in izip(gradient , pre_update , sq_sum_grad) ]
                parameter_updates += [ (ssg, rms_alpha*ssg + (np.cast['float32'](1.0)-rms_alpha)*(g**2)  ) \
                    for g , ssg in izip( gradient , sq_sum_grad) ]
                return parameter_updates
            elif momentum_type == "None":
                parameter_updates = [ ( p, p - l_rate*g) \
                    for p , g in izip(parameters , gradient ) ]
                return parameter_updates



       # define theano.functions
        self.train = theano.function( inputs = [ x_seq , y_hat , mask ,
                                                l_rate ,
                                                rms_alpha ,
                                                clip_range ,
                                                momentum
                                                ] ,
                                        updates = update(parameters , gradient) ,
                                        outputs = cost,
                                         )


        self.test  = theano.function( inputs = [x_seq , mask ]  , outputs =  y_out  )
        self.test_sof  = theano.function( inputs = [x_seq , mask ]  , outputs =  y_out_a  )

class RNN_layers: 
    def __init__(self , W , Wh , b , n_neurals ,in_seq , batch_size , act_type):
        
        def step(x_t , out_tm1 ): 
            out_t = F.activation_func( x_t  
                                        + T.dot( out_tm1 , Wh) + b.dimshuffle('x',0) , act_type)
            #out_t = ( T.dot( x_t , W ) + T.dot (out_tm1 , Wh) + b )
            return out_t  
        
        z_seq = T.dot( in_seq , W )
        a_init = theano.shared(np.asarray ( np.zeros( ( batch_size , n_neurals ) ) , 'float32' ))
  
        out_seq , _ = theano.scan(
                                fn=step, 
                                sequences =  z_seq , 
                                outputs_info =  [ a_init  ] 
                                )
        
        self.layer_out = out_seq
        
        self.test = theano.function(
                            inputs =  [in_seq] , 
                            outputs = out_seq )

class RNN_first_layer:
    def __init__(self , Wi , Whi , bi , n_neurals , x_seq , batch_size , act_type):
        def step(z_t , out_tm1):
            out_t = F.activation_func( z_t + T.dot(out_tm1 , Whi) + bi.dimshuffle('x' , 0 ) , act_type )
            return out_t

        z_seq = T.dot( x_seq , Wi )
        a_init = theano.shared(np.asarray ( np.zeros( ( batch_size , n_neurals ) ) , 'float32' ))

        out_seq , _ = theano.scan( fn=step,
                                  sequences = z_seq , 
                                  outputs_info = [ a_init ],
                                  truncate_gradient= -1 )
        self.layer_out = out_seq
   
     
class RNN_last_layer:
    def __init__(self , Wo , bo , a_seq ):

        y_seq = T.dot(a_seq , Wo) + bo.dimshuffle('x',0)
        self.layer_out = y_seq 

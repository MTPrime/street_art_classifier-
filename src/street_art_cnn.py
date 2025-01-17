from tensorflow import keras
from tensorflow.keras import callbacks
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Activation, Flatten
from tensorflow.keras.layers import Conv2D, MaxPooling2D
from tensorflow.keras.utils import to_categorical
# from keras_radam import RAdam
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import load_model
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.metrics import Precision, Recall 
import matplotlib.pyplot as plt
import argparse
import pandas as pd 

def create_data_generators(directory_path='data/train_test_split/', input_shape=(64, 64), batch_size=16):
    
    train_path = directory_path +'train'
    test_path = directory_path +'test'
    val_path = directory_path +'val'


    train_datagen = ImageDataGenerator(
            rescale=1./255,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True
            )
    
    test_datagen = ImageDataGenerator(
        rescale=1./255)

    train_generator = train_datagen.flow_from_directory(
        train_path,
        target_size=input_shape,
        batch_size=batch_size,
        class_mode='categorical',
        shuffle=False)
        
    val_generator = test_datagen.flow_from_directory(
        val_path,
        target_size=input_shape,
        batch_size=batch_size,
        class_mode='categorical',
        shuffle=False)

    test_generator = test_datagen.flow_from_directory(
        test_path,
        target_size=input_shape,
        batch_size=batch_size,
        class_mode='categorical',
        shuffle=False)

    return train_generator, test_generator, val_generator

def build_model(opt='adam', input_shape=(64, 64, 3), nb_classes = 5, neurons = 64, nb_filters = 12, pool_size = (2, 2), kernel_size = (3, 3)):
   
    model = Sequential() 

    model.add(Conv2D(nb_filters, (kernel_size[0], kernel_size[1]),
                    input_shape=input_shape,
                    padding = 'same',
                    name="conv-1")) 

    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=pool_size, name='pool-1'))

    model.add(Conv2D(nb_filters*2, 
                    (kernel_size[0], kernel_size[1]), padding='same', 
                    name='conv-2')) 
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=pool_size, name='pool-2'))

    model.add(Conv2D(nb_filters*3, 
                    (kernel_size[0], kernel_size[1]), padding='same',
                    name='conv-3')) 
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=pool_size, name='pool-3'))

    model.add(Conv2D(nb_filters*3, 
                    (kernel_size[0], kernel_size[1]), padding='same',
                    name='conv-4')) 
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=pool_size, name='pool-4'))

    model.add(Flatten())  
    model.add(Dense(neurons))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(nb_classes))
    if nb_classes == 2:
        model.add(Activation('sigmoid'))
    else:
        model.add(Activation('softmax'))
    
        
    model.compile(loss='categorical_crossentropy',
                optimizer=opt,
                metrics=['accuracy'])

    return model

def graph_loss(history, epochs):
    #Graphing
    # plot loss during training
    fig, ax = plt.subplots(2, figsize = (12, 8))
    ax[0].set_title('Loss')
    ax[0].set_xticks(range(0,epochs+1,5))
    ax[0].plot(history.history['loss'], label='train')
    ax[0].plot(history.history['val_loss'], label='test')
    ax[0].legend()

    # plot accuracy during training
    ax[1].set_xticks(range(0,epochs+1,5))
    ax[1].set_title('Accuracy')
    ax[1].plot(history.history['accuracy'], label='train')
    ax[1].plot(history.history['val_accuracy'], label='test')
    ax[1].legend()

    plt.savefig('images/model_loss.png')

def create_tensorboard(savename='5_class_new_arc_model_best.h5', monitor_metric='val_accuracty'):
    
    tensorboard = callbacks.TensorBoard(
        log_dir='logdir',
        histogram_freq=0, 
        write_graph=True,
        update_freq='epoch')


    savename = savename

    mc = callbacks.ModelCheckpoint(
        savename,
        monitor=monitor_metric, 
        verbose=0, 
        save_best_only=True, 
        mode='auto', 
        save_freq='epoch')
    
    return tensorboard, mc 

if __name__ == '__main__':
    #Settings
    batch_size = 20  
    nb_classes = 5   
    nb_epoch = 250              
    img_rows, img_cols = 100, 100  
    input_shape = (img_rows, img_cols, 3)  
    nb_filters = 32  
    pool_size = (2, 2)
    kernel_size = (3, 3) 
    neurons=128

    train_generator, test_generator, val_generator = create_data_generators(directory_path='data/train_test_split/', 
                                                                            input_shape=(img_rows,img_cols), 
                                                                            batch_size=batch_size)

    model = build_model(opt='adam', 
                            input_shape=input_shape, 
                            nb_classes = nb_classes, 
                            neurons = neurons, 
                            nb_filters = nb_filters, 
                            pool_size = pool_size, 
                            kernel_size = kernel_size)

    tensorboard, mc = create_tensorboard(savename='5_class_new_arc_model_best.h5', monitor_metric='val_accuracty')
    
    print(model.summary())

    history = model.fit_generator(train_generator,
                                      steps_per_epoch=600,
                                      epochs=nb_epoch,
                                      validation_data=val_generator,
                                      validation_steps=100,
                                      callbacks=[mc, tensorboard])

    #Saves the loss and accuracy as a csv
    df = pd.DataFrame.from_dict(history.history)
    df.to_csv('model_loss_and_accuracy.csv')

    #Saves the final model as well.    
    model.save_weights('5_class_new_arc_weights_clean.h5')
    model.save('5_class_new_arc_model_clean.h5')

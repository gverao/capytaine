# -*- coding: utf-8 -*-
"""
Example file based on Malenica 1995:
Š. Malenica, P.J. Clark, B. Molin,
Wave and current forces on a vertical cylinder free to surge and sway,
Applied Ocean Research,
Volume 17, Issue 2,
1995,
Pages 79-90,
ISSN 0141-1187,
https://doi.org/10.1016/0141-1187(95)00002-I.

This script is generated by Maritime Technology Division (MTD) of Ghent University, Belgium. 
Please refer to following papers:

I. Herdayanditya, L. Donatini, G. Verao Fernandez, A. B. K. Pribadi, and P. Rauwoens, 
“Waves-current effect investigation on monopile excitation force employing approximate 
forward speed approach,” in 6th MASHCON : international conference on ship manoeuvring 
in shallow and confined water with special focus on port manoeuvres, Glasgow, UK, 2022, pp. 73–80.
http://hdl.handle.net/1854/LU-8756871

L. Donatini, I. Herdayanditya, G. Verao Fernandez, A. B. K. Pribadi, E. Lataire, 
and G. Delefortrie, “Implementation of forward speed effects on an open source seakeeping 
solver,” in 6th MASHCON : international conference on ship manoeuvring in shallow and confined 
water with special focus on port manoeuvres, Glasgow, UK, 2022, pp. 20–33.
http://hdl.handle.net/1854/LU-8756868

"""
import matplotlib.pyplot as plt
import numpy as np
import capytaine as cpt
import xarray as xr

def generate_cylinder(Length, Radius, Center, Resolution):
    cylinder = cpt.FloatingBody(mesh=cpt.mesh_vertical_cylinder(length=Length, 
                radius=Radius, center=Center, resolution=Resolution))
    cylinder.center_of_mass = np.array([0, 0, 0])
    cylinder.rotation_center = np.array([0, 0, 0])
    cylinder.add_all_rigid_body_dofs()
    cylinder.inertia_matrix = cylinder.compute_rigid_body_inertia()
    cylinder.add_all_rigid_body_dofs()
    cylinder.hydrostatic_stiffness = cylinder.compute_hydrostatic_stiffness()
    cylinder.keep_immersed_part(free_surface=0.0, sea_bottom=-Radius)
    cylinder.show()
    return cylinder

def run_simulation(cylinder,gravity, water_density, omega_range, wave_direction, water_depth, forward_speed):
    data_matrix = xr.Dataset(coords={
                    'omega': omega_range,
                    'wave_direction': wave_direction,
                    'radiating_dof': list(cylinder.dofs),
                    'water_depth': water_depth,
                    'rho': [water_density],
                    'g': [gravity],
                    'forward_speed': [forward_speed]
                })
    solver = cpt.BEMSolver()
    dataset = cpt.BEMSolver.fill_dataset(solver, data_matrix, cylinder, n_jobs=1)
    return dataset

if __name__ =='__main__':
    radius = 1.0 # cylinder radius [m]
    length =0.99*radius # cylinder length [m]
    center = (0, 0, -0.5) 
    resolution = (20, 20, 20)
    gravity = 9.81
    water_density = 1025.
    wave_direction = 0
    ko=np.linspace(0.2,2,25)
    omega_range   =np.sqrt(gravity*ko*np.tanh(ko*1))
    froude_number = np.array([0, 0.05, -0.05])
    water_depth = radius
    forward_speed = froude_number*np.sqrt(gravity*radius)
    cylinder = generate_cylinder(length, radius, center, resolution)
    dataset_all = []
    for jj in range(len(forward_speed)):
        dataset = run_simulation(cylinder, gravity, water_density, omega_range, wave_direction, water_depth, forward_speed[jj]) # run simulation
        dataset['excitation_force']=dataset['Froude_Krylov_force']+dataset['diffraction_force']
        dataset_all.append(dataset)    
    [dataset1, dataset2, dataset3] = dataset_all
    ## PLOT THE RESULTS
    ## EXCITATION FORCE
    plt.figure()
    plt.plot(ko,np.abs(dataset1.excitation_force.values[:,0,0])/(1025*9.81))
    plt.plot(ko,np.abs(dataset2.excitation_force.values[:,0,0])/(1025*9.81))
    plt.plot(ko,np.abs(dataset3.excitation_force.values[:,0,0])/(1025*9.81))
    plt.legend(['Fr = 0','Fr = 0.05','Fr = -0.05'])
    plt.xlabel(r'$k_o a$ '); plt.ylabel(r'$Fe_{1}/\rho g a^2$ (Capytaine)')
    I= [0]; J= [0]
    for ii in I: 
        for jj in J:
            ## ADDED MASS 
            plt.figure()
            plt.title('Added Mass Capytaine'+str(ii+1)+str(jj+1))
            plt.plot(ko,dataset1.added_mass.values[:,ii,jj]/1025)
            plt.plot(ko,dataset2.added_mass.values[:,ii,jj]/1025)
            plt.plot(ko,dataset3.added_mass.values[:,ii,jj]/1025)
            plt.legend(['Fr = 0','Fr = 0.05','Fr = -0.05'])
            plt.xlabel(r'$k_o a$ '); plt.ylabel(r'$a_{11}/\rho a^3$ (Capytaine)')
            plt.ylim([0,4])
            ### RADIATION DAMPING
            wec1=dataset1.omega.values#-ko*dataset1RAO.forward_speed.values
            wec2=dataset2.omega.values-ko*froude_number[1]
            wec3=dataset3.omega.values-ko*froude_number[2]
            plt.figure()
            plt.title('Damping Capytaine'+str(ii+1)+str(jj+1))
            plt.plot(ko,dataset1.radiation_damping.values[:,ii,jj]/(1025*wec1))
            plt.plot(ko,dataset2.radiation_damping.values[:,ii,jj]/(1025*wec2))
            plt.plot(ko,dataset3.radiation_damping.values[:,ii,jj]/(1025*wec3))
            plt.legend(['Fr = 0','Fr = 0.05','Fr = -0.05'])
            plt.xlabel(r'$k_o a$'); plt.ylabel(r'$b_{11}/\rho a^3 \omega_e$ (Capytaine)')
            plt.ylim([0,2.5])
    plt.show()
    
    
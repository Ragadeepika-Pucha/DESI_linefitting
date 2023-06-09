"""
This script consists of funcitons for fitting emission-lines.
The different functions are divided into different classes for different emission lines.

Author : Ragadeepika Pucha
Version : 2023, May 24
"""

###################################################################################################

import numpy as np

from astropy.modeling import fitting
from astropy.modeling.models import Gaussian1D, Polynomial1D, Const1D

import fit_utils
import measure_fits as mfit

###################################################################################################

class fit_sii_lines:
    """
    Different functions associated with [SII]6716, 6731 doublet fitting:
        1) fit_one_component(lam_sii, flam_sii, ivar_sii, fit_cont)
        2) fit_two_components(lam_sii, flam_sii, ivar_sii, fit_cont)
    """
    
    def fit_one_component(lam_sii, flam_sii, ivar_sii, fit_cont = True):
        """
        Function to fit a single component to [SII]6716, 6731 doublet.
        
        Parameters
        ----------
        lam_sii : numpy array
            Wavelength array of the [SII] region where the fits need to be performed.
        
        flam_sii : numpy array
            Flux array of the spectra in the [SII] region.

        ivar_sii : numpy array
            Inverse variance array of the spectra in the [SII] region.

        Returns
        -------
        gfit : Astropy model
            Best-fit 1 component model

        rchi2: float
            Reduced chi2 of the best-fit
        """
        
        ## Initial estimate of amplitudes
        amp_sii = max(flam_sii)

        ## Initial gaussian fits  
        ## Set default sigma values to 130 km/s ~ 2.9 in wavelength space
        ## Set amplitudes > 0, sigma > 40 km/s
        
        g_sii6716 = Gaussian1D(amplitude = amp_sii, mean = 6718.294, \
                               stddev = 2.9, name = 'sii6716', \
                               bounds = {'amplitude' : (0.0, None), 'stddev' : (0.8, None)})
        g_sii6731 = Gaussian1D(amplitude = amp_sii, mean = 6732.673, \
                               stddev = 2.9, name = 'sii6731', \
                               bounds = {'amplitude' : (0.0, None), 'stddev' : (0.8, None)})

        ## Tie means of the two gaussians
        def tie_mean_sii(model):
            return (model['sii6716'].mean + 14.329)

        g_sii6731.mean.tied = tie_mean_sii

        ## Tie standard deviations of the two gaussians
        def tie_std_sii(model):
            return ((model['sii6716'].stddev)*(model['sii6731'].mean/model['sii6716'].mean))

        g_sii6731.stddev.tied = tie_std_sii
        
        if (fit_cont == True):
            ## Continuum as a constant
            cont = Const1D(amplitude = 0.0, name = 'sii_cont')

            ## Initial Gaussian fit
            g_init = cont + g_sii6716 + g_sii6731
            fitter_1comp = fitting.LevMarLSQFitter()

            ## Fit
            gfit_1comp = fitter_1comp(g_init, lam_sii, flam_sii, \
                                weights = np.sqrt(ivar_sii), maxiter = 1000)
            rchi2_1comp = mfit.calculate_red_chi2(flam_sii, gfit_1comp(lam_sii),\
                                                       ivar_sii, n_free_params = 5)
        else:
            ## Initial Gaussian fit
            g_init = g_sii6716 + g_sii6731
            fitter_1comp = fitting.LevMarLSQFitter()

            ## Fit
            gfit_1comp = fitter_1comp(g_init, lam_sii, flam_sii, \
                                weights = np.sqrt(ivar_sii), maxiter = 1000)
            rchi2_1comp = mfit.calculate_red_chi2(flam_sii, gfit_1comp(lam_sii),\
                                                       ivar_sii, n_free_params = 4)
                
        return (gfit_1comp, rchi2_1comp)
    
####################################################################################################
    
    def fit_two_components(lam_sii, flam_sii, ivar_sii, fit_cont = True):
        """
        Function to fit two components to [SII]6716, 6731 doublet.
        
        Parameters
        ----------
        lam_sii : numpy array
            Wavelength array of the [SII] region where the fits need to be performed.
        
        flam_sii : numpy array
            Flux array of the spectra in the [SII] region.

        ivar_sii : numpy array
            Inverse variance array of the spectra in the [SII] region.

        Returns
        -------
        gfit : Astropy model
            Best-fit 2 component model

        rchi2: float
            Reduced chi2 of the best-fit
        """
        
        ## Initial estimate of amplitudes
        amp_sii = max(flam_sii)
        
        ## Initial gaussian fits
        ## Default values of sigma ~ 130 km/s ~ 2.9
        ## Set amplitudes > 0, sigma > 40 km/s
        ## Sigma of outflows >~ 80 km/s
        g_sii6716 = Gaussian1D(amplitude = amp_sii/3, mean = 6718.294, \
                               stddev = 2.9, name = 'sii6716', \
                              bounds = {'amplitude' : (0.0, None), 'stddev' : (0.8, None)})
        g_sii6731 = Gaussian1D(amplitude = amp_sii/3, mean = 6732.673, \
                               stddev = 2.9, name = 'sii6731', \
                              bounds = {'amplitude' : (0.0, None), 'stddev' : (0.8, None)})

        g_sii6716_out = Gaussian1D(amplitude = amp_sii/6, mean = 6718.294, \
                                   stddev = 4.0, name = 'sii6716_out', \
                                   bounds = {'amplitude' : (0.0, None), 'stddev' : (1.6, None)})
        g_sii6731_out = Gaussian1D(amplitude = amp_sii/6, mean = 6732.673, \
                                   stddev = 4.0, name = 'sii6731_out', \
                                   bounds = {'amplitude' : (0.0, None), 'stddev' : (1.6, None)})

        ## Tie means of the main gaussian components
        def tie_mean_sii(model):
            return (model['sii6716'].mean + 14.379)

        g_sii6731.mean.tied = tie_mean_sii

        ## Tie standard deviations of the main gaussian components
        def tie_std_sii(model):
            return ((model['sii6716'].stddev)*\
                    (model['sii6731'].mean/model['sii6716'].mean))

        g_sii6731.stddev.tied = tie_std_sii

        ## Tie means of the outflow components
        def tie_mean_sii_out(model):
            return (model['sii6716_out'].mean + 14.379)

        g_sii6731_out.mean.tied = tie_mean_sii_out

        ## Tie standard deviations of the outflow components
        def tie_std_sii_out(model):
            return ((model['sii6716_out'].stddev)*\
                    (model['sii6731_out'].mean/model['sii6716_out'].mean))

        g_sii6731_out.stddev.tied = tie_std_sii_out

        ## Tie amplitudes of all the four components
        def tie_amp_sii(model):
            return ((model['sii6731'].amplitude/model['sii6716'].amplitude)*\
                    model['sii6716_out'].amplitude)

        g_sii6731_out.amplitude.tied = tie_amp_sii
        
        if (fit_cont == True):
            ## Continuum
            cont = Const1D(amplitude = 0.0, name = 'sii_cont')

            ## Initial gaussian
            g_init = cont + g_sii6716 + g_sii6731 + g_sii6716_out + g_sii6731_out
            fitter_2comp = fitting.LevMarLSQFitter()

            gfit_2comp = fitter_2comp(g_init, lam_sii, flam_sii, \
                                weights = np.sqrt(ivar_sii), maxiter = 1000)
            rchi2_2comp = mfit.calculate_red_chi2(flam_sii, gfit_2comp(lam_sii), \
                                                       ivar_sii, n_free_params = 8)
        else:
            ## Initial gaussian
            g_init = g_sii6716 + g_sii6731 + g_sii6716_out + g_sii6731_out
            fitter_2comp = fitting.LevMarLSQFitter()

            gfit_2comp = fitter_2comp(g_init, lam_sii, flam_sii, \
                                weights = np.sqrt(ivar_sii), maxiter = 1000)
            rchi2_2comp = mfit.calculate_red_chi2(flam_sii, gfit_2comp(lam_sii), \
                                                       ivar_sii, n_free_params = 7)
        
        return (gfit_2comp, rchi2_2comp)    
    
####################################################################################################
####################################################################################################

class fit_oiii_lines:
    """
    Different functions associated with [OIII]4959, 5007 doublet fitting:
        1) fit_one_component(lam_oiii, flam_oiii, ivar_oiii, fit_cont)
        2) fit_two_components(lam_oiii, flam_oiii, ivar_oiii, fit_cont)
    """

    def fit_one_component(lam_oiii, flam_oiii, ivar_oiii, fit_cont = True):
        """
        Function to fit a single component to [OIII]4959,5007 doublet.
        
        Parameters
        ----------
        lam_oiii : numpy array
            Wavelength array of the [OIII] region where the fits need to be performed.

        flam_oiii : numpy array
            Flux array of the spectra in the [OIII] region.

        ivar_oiii : numpy array
            Inverse variance array of the spectra in the [OIII] region.

        Returns
        -------
        gfit : Astropy model
            Best-fit 1 component model

        rchi2: float
            Reduced chi2 of the best-fit
        """
        
        # Find initial estimates of amplitudes
        amp_oiii4959 = np.max(flam_oiii[(lam_oiii >= 4959)&(lam_oiii <= 4961)])
        amp_oiii5007 = np.max(flam_oiii[(lam_oiii >= 5007)&(lam_oiii <= 5009)])

        ## Initial gaussian fits
        ## Set default values of sigma ~ 130 km/s ~ 2.1
        ## Set amplitudes > 0
        g_oiii4959 = Gaussian1D(amplitude = amp_oiii4959, mean = 4960.295, \
                                stddev = 1.0, name = 'oiii4959', \
                                bounds = {'amplitude' : (0.0, None), 'stddev' : (0.6, None)})
        g_oiii5007 = Gaussian1D(amplitude = amp_oiii5007, mean = 5008.239, \
                                stddev = 1.0, name = 'oiii5007', \
                                bounds = {'amplitude' : (0.0, None), 'stddev' : (0.6, None)})

        ## Tie Means of the two gaussians
        def tie_mean_oiii(model):
            return (model['oiii4959'].mean + 47.934)

        g_oiii5007.mean.tied = tie_mean_oiii

        ## Tie Amplitudes of the two gaussians
        def tie_amp_oiii(model):
            return (model['oiii4959'].amplitude*2.98)

        g_oiii5007.amplitude.tied = tie_amp_oiii

        ## Tie standard deviations in velocity space
        def tie_std_oiii(model):
            return ((model['oiii4959'].stddev)*\
                    (model['oiii5007'].mean/model['oiii4959'].mean))

        g_oiii5007.stddev.tied = tie_std_oiii
        
        if (fit_cont == True):
            ## Continuum
            cont = Const1D(amplitude = 0.0, name = 'oiii_cont')

            ## Initial Gaussian fit
            g_init = cont + g_oiii4959 + g_oiii5007

            ## Fitter
            fitter_1comp = fitting.LevMarLSQFitter()

            gfit_1comp = fitter_1comp(g_init, lam_oiii, flam_oiii, \
                                weights = np.sqrt(ivar_oiii), maxiter = 1000)
            rchi2_1comp = mfit.calculate_red_chi2(flam_oiii, gfit_1comp(lam_oiii), \
                                                       ivar_oiii, n_free_params = 4) 
            
        else:
            ## Initial Gaussian fit
            g_init = g_oiii4959 + g_oiii5007

            ## Fitter
            fitter_1comp = fitting.LevMarLSQFitter()

            gfit_1comp = fitter_1comp(g_init, lam_oiii, flam_oiii, \
                                weights = np.sqrt(ivar_oiii), maxiter = 1000)
            rchi2_1comp = mfit.calculate_red_chi2(flam_oiii, gfit_1comp(lam_oiii), \
                                                       ivar_oiii, n_free_params = 3)
        
        return (gfit_1comp, rchi2_1comp)
    
####################################################################################################

    def fit_two_components(lam_oiii, flam_oiii, ivar_oiii, fit_cont = True):
        """
        Function to fit a two components to [OIII]4959,5007 doublet.
        
        Parameters
        ----------
        lam_oiii : numpy array
            Wavelength array of the [OIII] region where the fits need to be performed.

        flam_oiii : numpy array
            Flux array of the spectra in the [OIII] region.

        ivar_oiii : numpy array
            Inverse variance array of the spectra in the [OIII] region.

        Returns
        -------
        gfit : Astropy model
            Best-fit 2 component model

        rchi2: float
            Reduced chi2 of the best-fit
        """
        
        # Find initial estimates of amplitudes
        amp_oiii4959 = np.max(flam_oiii[(lam_oiii >= 4959)&(lam_oiii <= 4961)])
        amp_oiii5007 = np.max(flam_oiii[(lam_oiii >= 5007)&(lam_oiii <= 5009)])
        
        ## Initial gaussians
        ## Set default values of sigma ~ 130 km/s ~ 2.1
        ## Set amplitudes > 0
        g_oiii4959 = Gaussian1D(amplitude = amp_oiii4959/2, mean = 4960.295, \
                                stddev = 1.0, name = 'oiii4959', \
                                bounds = {'amplitude' : (0.0, None), 'stddev' : (0.6, None)})
        g_oiii5007 = Gaussian1D(amplitude = amp_oiii5007/2, mean = 5008.239, \
                                stddev = 1.0, name = 'oiii5007', \
                                bounds = {'amplitude' : (0.0, None), 'stddev' : (0.6, None)})

        g_oiii4959_out = Gaussian1D(amplitude = amp_oiii4959/4, mean = 4960.295, \
                                    stddev = 6.0, name = 'oiii4959_out', \
                                    bounds = {'amplitude' : (0.0, None), 'stddev' : (1.2, None)})
        g_oiii5007_out = Gaussian1D(amplitude = amp_oiii5007/4, mean = 5008.239, \
                                    stddev = 6.0, name = 'oiii5007_out', \
                                    bounds = {'amplitude' : (0.0, None), 'stddev' : (1.2, None)})

        ## Tie Means of the two gaussians
        def tie_mean_oiii(model):
            return (model['oiii4959'].mean + 47.934)

        g_oiii5007.mean.tied = tie_mean_oiii

        ## Tie Amplitudes of the two gaussians
        def tie_amp_oiii(model):
            return (model['oiii4959'].amplitude*2.98)

        g_oiii5007.amplitude.tied = tie_amp_oiii

        ## Tie standard deviations in velocity space
        def tie_std_oiii(model):
            return ((model['oiii4959'].stddev)*\
                    (model['oiii5007'].mean/model['oiii4959'].mean))

        g_oiii5007.stddev.tied = tie_std_oiii

        ## Tie Means of the two gaussian outflow components
        def tie_mean_oiii_out(model):
            return (model['oiii4959_out'].mean + 47.934)

        g_oiii5007_out.mean.tied = tie_mean_oiii_out

        ## Tie Amplitudes of the two gaussian outflow components
        def tie_amp_oiii_out(model):
            return (model['oiii4959_out'].amplitude*2.98)

        g_oiii5007_out.amplitude.tied = tie_amp_oiii_out

        ## Tie standard deviations of the outflow components in the velocity space
        def tie_std_oiii_out(model):
            return ((model['oiii4959_out'].stddev)*\
        (model['oiii5007_out'].mean/model['oiii4959_out'].mean))

        g_oiii5007_out.stddev.tied = tie_std_oiii_out
        
        if (fit_cont == True):
            ## Continuum
            cont = Const1D(amplitude = 0.0, name = 'oiii_cont')

            ## Initial Gaussian fit
            g_init = cont + g_oiii4959 + g_oiii5007 + g_oiii4959_out + g_oiii5007_out

            ## Fitter
            fitter_2comp = fitting.LevMarLSQFitter()

            gfit_2comp = fitter_2comp(g_init, lam_oiii, flam_oiii, \
                                weights = np.sqrt(ivar_oiii), maxiter = 1000)
            rchi2_2comp = mfit.calculate_red_chi2(flam_oiii, gfit_2comp(lam_oiii), \
                                                       ivar_oiii, n_free_params = 7)
        else:
            ## Initial Gaussian fit
            g_init = g_oiii4959 + g_oiii5007 + g_oiii4959_out + g_oiii5007_out

            ## Fitter
            fitter_2comp = fitting.LevMarLSQFitter()

            gfit_2comp = fitter_2comp(g_init, lam_oiii, flam_oiii, \
                                weights = np.sqrt(ivar_oiii), maxiter = 1000)
            rchi2_2comp = mfit.calculate_red_chi2(flam_oiii, gfit_2comp(lam_oiii), \
                                                       ivar_oiii, n_free_params = 6)
        
        return (gfit_2comp, rchi2_2comp)

####################################################################################################
####################################################################################################

class fit_hb_line:
    """
    Different functions associated with fitting the Hbeta emission-line, 
    including a broad-component:
        1) fit_free_one_component(lam_hb, flam_hb, ivar_hb, sii_bestfit, frac_temp, fit_cont)
        2) fit_free_two_components(lam_hb, flam_hb, ivar_hb, sii_bestfit, frac_temp, fit_cont)
        3) fit_fixed_one_component(lam_hb, flam_hb, ivar_hb, sii_bestfit, fit_cont)
        4) fit_fixed_two_components(lam_hb, flam_hb, ivar_hb, sii_bestfit, fit_cont)
    """
    
    def fit_free_one_component(lam_hb, flam_hb, ivar_hb, sii_bestfit, \
                               frac_temp = 60, fit_cont = True):
        """
        Function to fit Hb emission lines - with a single narrow component.
        The width is set to be within some percent (default = 60%) of [SII] width.
        This is only when [SII] does not have extra components.
        
        The code fits both with and without broad-component fits and picks the best version.
        The broad-component is allowed if the chi2 improves by 20%
        
        Parameters
        ----------
        lam_hb : numpy array
            Wavelength array of the Hb region where the fits need to be performed.

        flam_hb : numpy array
            Flux array of the spectra in the Hb region.

        ivar_hb : numpy array
            Inverse variance array of the spectra in the Hb region.

        sii_bestfit : astropy model fit
            Best fit for [SII] emission lines.
            Sigma of narrow Hb bounds are set to be within some percent of [SII] width.

        frac_temp : float
            The %age of [SII] width within which narrow Hbeta width can vary

        Returns
        -------
        gfit : Astropy model
            Best-fit "without-broad" or "with-broad" component

        rchi2: float
            Reduced chi2 of the best-fit
            
        flag_bits : numpy array
            Array of flag bits for free one-component Hbeta fitting
                0 : Free one component fitting
                4 : chi^2 for broad-component fit improves by 20%
                5 : sigma (Hbeta broad) < sigma (Hbeta narrow)
                
        n_dof : int
            Number of degrees of freedom
        """

        flag_bits = np.array([])
        
        ## Template fit
        temp_std = sii_bestfit['sii6716'].stddev.value
        temp_std_kms = mfit.lamspace_to_velspace(temp_std, sii_bestfit['sii6716'].mean.value)

        min_std_kms = temp_std_kms - ((frac_temp/100)*temp_std_kms)
        max_std_kms = temp_std_kms + ((frac_temp/100)*temp_std_kms)

        min_std = mfit.velspace_to_lamspace(min_std_kms, 4862.683)
        max_std = mfit.velspace_to_lamspace(max_std_kms, 4862.683)

        ## Initial estimate of amplitude
        amp_hb = np.max(flam_hb)

        ## No outflow components
        ## Single component fit
        g_hb_n = Gaussian1D(amplitude = amp_hb, mean = 4862.683, \
                          stddev = temp_std, name = 'hb_n', \
                          bounds = {'amplitude' : (0.0, None), 'stddev' : (0.5, None)})

        g_hb_n.stddev.bounds = (min_std, max_std)
        
        if (fit_cont == True):
            ## Continuum
            cont = Const1D(amplitude = 0.0, name = 'hb_cont')

            g_hb = cont + g_hb_n

            #####################################################################################
            ########################### Fit without broad component #############################

            ## Initial fit
            g_init = g_hb 
            fitter_no_broad = fitting.LevMarLSQFitter()

            gfit_no_broad = fitter_no_broad(g_init, lam_hb, flam_hb, \
                                            weights = np.sqrt(ivar_hb), maxiter = 1000)


            rchi2_no_broad = mfit.calculate_red_chi2(flam_hb, gfit_no_broad(lam_hb), \
                                                         ivar_hb, n_free_params = 4)

            #####################################################################################
            ########################### Fit with broad component ################################

            ## Two component fit
            g_hb_b = Gaussian1D(amplitude = amp_hb/3, mean = 4862.683, \
                                stddev = 3.0, name = 'hb_b', \
                                bounds = {'amplitude' : (0.0, None), 'stddev' : (1.0, None)})

            ## Initial fit
            g_init = g_hb + g_hb_b 
            fitter_broad = fitting.LevMarLSQFitter()

            gfit_broad = fitter_broad(g_init, lam_hb, flam_hb, \
                                      weights = np.sqrt(ivar_hb), maxiter = 1000)

            rchi2_broad = mfit.calculate_red_chi2(flam_hb, gfit_broad(lam_hb), \
                                                  ivar_hb, n_free_params = 7)

            #####################################################################################
            #####################################################################################
            
        else:
            g_hb = g_hb_n

            #####################################################################################
            ########################### Fit without broad component #############################

            ## Initial fit
            g_init = g_hb 
            fitter_no_broad = fitting.LevMarLSQFitter()

            gfit_no_broad = fitter_no_broad(g_init, lam_hb, flam_hb, \
                                            weights = np.sqrt(ivar_hb), maxiter = 1000)


            rchi2_no_broad = mfit.calculate_red_chi2(flam_hb, gfit_no_broad(lam_hb), \
                                                         ivar_hb, n_free_params = 3)

            #####################################################################################
            ########################### Fit with broad component ################################

            ## Two component fit
            g_hb_b = Gaussian1D(amplitude = amp_hb/3, mean = 4862.683, \
                                stddev = 3.0, name = 'hb_b', \
                                bounds = {'amplitude' : (0.0, None), 'stddev' : (1.0, None)})

            ## Initial fit
            g_init = g_hb + g_hb_b 
            fitter_broad = fitting.LevMarLSQFitter()

            gfit_broad = fitter_broad(g_init, lam_hb, flam_hb, \
                                      weights = np.sqrt(ivar_hb), maxiter = 1000)

            rchi2_broad = mfit.calculate_red_chi2(flam_hb, gfit_broad(lam_hb), \
                                                  ivar_hb, n_free_params = 6)

            #####################################################################################
            #####################################################################################

        ## Select the best-fit based on rchi2
        ## If the rchi2 of 2-component is better by 20%, then the 2-component fit is picked.
        ## Otherwise, 1-component fit is the best fit.
        del_rchi2 = ((rchi2_no_broad - rchi2_broad)/rchi2_no_broad)*100
        
        sig_hb_n = mfit.lamspace_to_velspace(gfit_broad['hb_n'].stddev.value, \
                                             gfit_broad['hb_n'].mean.value)
        sig_hb_b = mfit.lamspace_to_velspace(gfit_broad['hb_b'].stddev.value, \
                                             gfit_broad['hb_b'].mean.value)
        
        ## Set flags 
        flag_bits = np.append(flag_bits, 0)
        if (del_rchi2 >= 20):
            flag_bits = np.append(flag_bits, 4)
        if (sig_hb_b < sig_hb_n):
            flag_bits = np.append(flag_bits, 5)
        if (sig_hb_n < 40):
            flag_bits = np.append(flag_bits, 9)

        flag_bits = np.sort(flag_bits.astype(int))
        
        if ((del_rchi2 >= 20)&(sig_hb_b > sig_hb_n)&(sig_hb_n >= 40.)):
            if (fit_cont == True):
                n_dof = 7
            else:
                n_dof = 6
                
            return (gfit_broad, rchi2_broad, flag_bits, n_dof)
        else:
            if (fit_cont == True):
                n_dof = 4
            else:
                n_dof = 3
            
            return (gfit_no_broad, rchi2_no_broad, flag_bits, n_dof)
        
####################################################################################################

    def fit_free_two_components(lam_hb, flam_hb, ivar_hb, sii_bestfit, \
                                frac_temp = 60., fit_cont = True):
        """
        Function to fit Hb emission lines - with a single+outflow components.
        The width is set to be within some percent (default = 60%) of [SII] width.
        This is when [SII] has narrow+outflow components.
        
        The code fits both with and without broad-component fits and picks the best version.
        The broad-component is allowed if the chi2 improves by 20%
        
        Parameters
        ----------
        lam_hb : numpy array
            Wavelength array of the Hb region where the fits need to be performed.

        flam_hb : numpy array
            Flux array of the spectra in the Hb region.

        ivar_hb : numpy array
            Inverse variance array of the spectra in the Hb region.

        sii_bestfit : astropy model fit
            Best fit for [SII] emission lines.
            Sigma of narrow Hb bounds are set to be within some percent of [SII] width.

        frac_temp : float
            The %age of [SII] width within which narrow Hbeta width can vary

        Returns
        -------
        gfit : Astropy model
            Best-fit "without-broad" or "with-broad" component

        rchi2: float
            Reduced chi2 of the best-fit
            
        flag_bits : numpy array
            Array of flag bits for free two-component Hbeta fitting
                2 : Free two component fitting
                4 : chi^2 for broad-component fit improves by 20%
                5 : sigma (Hbeta broad) < sigma (Hbeta narrow)
                6 : sigma (Hbeta outflow) > sigma (Hbeta broad)
                
        n_dof : int
            Number of degrees of freedom
        """
        
        flag_bits = np.array([])
        
        ## Template fit
        temp_std = sii_bestfit['sii6716'].stddev.value
        temp_std_kms = mfit.lamspace_to_velspace(temp_std, sii_bestfit['sii6716'].mean.value)

        min_std_kms = temp_std_kms - ((frac_temp/100)*temp_std_kms)
        max_std_kms = temp_std_kms + ((frac_temp/100)*temp_std_kms)

        min_std = mfit.velspace_to_lamspace(min_std_kms, 4862.683)
        max_std = mfit.velspace_to_lamspace(max_std_kms, 4862.683)

        ## Initial estimate of amplitude
        amp_hb = np.max(flam_hb)
        
        ## Outflow components
        temp_out_std = sii_bestfit['sii6716_out'].stddev.value
        temp_out_std_kms = mfit.lamspace_to_velspace(temp_out_std, \
                                                     sii_bestfit['sii6716_out'].mean.value)

        min_out_kms = temp_out_std_kms - ((frac_temp/100)*temp_out_std_kms)
        max_out_kms = temp_out_std_kms + ((frac_temp/100)*temp_out_std_kms)

        min_out = mfit.velspace_to_lamspace(min_out_kms, 4862.683)
        max_out = mfit.velspace_to_lamspace(max_out_kms, 4862.683)

        ## Two component fit for the narrow Hb
        g_hb_n = Gaussian1D(amplitude = amp_hb/2, mean = 4862.683, \
                            stddev = temp_std, name = 'hb_n', \
                            bounds = {'amplitude' : (0.0, None), 'stddev' : (0.5, None)})
        g_hb_out = Gaussian1D(amplitude = amp_hb/4, mean = 4862.683, \
                              stddev = temp_out_std, name = 'hb_out', \
                              bounds = {'amplitude' : (0.0, None), 'stddev' : (0.5, None)})

        g_hb_n.stddev.bounds = (min_std, max_std)
        g_hb_out.stddev.bounds = (min_out, max_out)
        
        if (fit_cont == True):
            ## Continuum
            cont = Const1D(amplitude = 0.0, name = 'hb_cont')

            g_hb = cont + g_hb_n + g_hb_out

            #####################################################################################
            ########################### Fit without broad component #############################

            ## Initial fit
            g_init = g_hb 
            fitter_no_broad = fitting.LevMarLSQFitter()

            gfit_no_broad = fitter_no_broad(g_init, lam_hb, flam_hb, \
                                            weights = np.sqrt(ivar_hb), maxiter = 1000)


            rchi2_no_broad = mfit.calculate_red_chi2(flam_hb, gfit_no_broad(lam_hb), \
                                                         ivar_hb, n_free_params = 7)

            #####################################################################################
            ########################### Fit with broad component ################################

            ## Two component fit
            g_hb_b = Gaussian1D(amplitude = amp_hb/3, mean = 4862.683, \
                                stddev = 3.0, name = 'hb_b', \
                                bounds = {'amplitude' : (0.0, None), 'stddev' : (1.0, None)})

            ## Initial fit
            g_init = g_hb + g_hb_b 
            fitter_broad = fitting.LevMarLSQFitter()

            gfit_broad = fitter_broad(g_init, lam_hb, flam_hb, \
                                      weights = np.sqrt(ivar_hb), maxiter = 1000)

            rchi2_broad = mfit.calculate_red_chi2(flam_hb, gfit_broad(lam_hb), \
                                                  ivar_hb, n_free_params = 10)

            #####################################################################################
            #####################################################################################
            
        else:
            g_hb = g_hb_n + g_hb_out

            #####################################################################################
            ########################### Fit without broad component #############################

            ## Initial fit
            g_init = g_hb 
            fitter_no_broad = fitting.LevMarLSQFitter()

            gfit_no_broad = fitter_no_broad(g_init, lam_hb, flam_hb, \
                                            weights = np.sqrt(ivar_hb), maxiter = 1000)


            rchi2_no_broad = mfit.calculate_red_chi2(flam_hb, gfit_no_broad(lam_hb), \
                                                         ivar_hb, n_free_params = 6)

            #####################################################################################
            ########################### Fit with broad component ################################

            ## Two component fit
            g_hb_b = Gaussian1D(amplitude = amp_hb/3, mean = 4862.683, \
                                stddev = 3.0, name = 'hb_b', \
                                bounds = {'amplitude' : (0.0, None), 'stddev' : (1.0, None)})

            ## Initial fit
            g_init = g_hb + g_hb_b 
            fitter_broad = fitting.LevMarLSQFitter()

            gfit_broad = fitter_broad(g_init, lam_hb, flam_hb, \
                                      weights = np.sqrt(ivar_hb), maxiter = 1000)

            rchi2_broad = mfit.calculate_red_chi2(flam_hb, gfit_broad(lam_hb), \
                                                  ivar_hb, n_free_params = 9)

            #####################################################################################
            #####################################################################################
        
        ## If broad-sigma < outflow-sigma -- exchange the gaussians.
        sigma_hb_b = mfit.lamspace_to_velspace(gfit_broad['hb_b'].stddev.value, \
                                              gfit_broad['hb_b'].mean.value)
        
        sigma_hb_out = mfit.lamspace_to_velspace(gfit_broad['hb_out'].stddev.value, \
                                                gfit_broad['hb_out'].mean.value)
        
        if (sigma_hb_b < sigma_hb_out):
            flag_bits = np.append(flag_bits, 6)
            g_hb_n = Gaussian1D(amplitude = gfit_broad['hb_n'].amplitude, \
                                mean = gfit_broad['hb_n'].mean, \
                                stddev = gfit_broad['hb_n'].stddev, name = 'hb_n')
            
            g_hb_out = Gaussian1D(amplitude = gfit_broad['hb_b'].amplitude, \
                                 mean = gfit_broad['hb_b'].mean, \
                                 stddev = gfit_broad['hb_b'].stddev, name = 'hb_out')
            
            g_hb_b = Gaussian1D(amplitude = gfit_broad['hb_out'].amplitude, \
                               mean = gfit_broad['hb_out'].mean, \
                               stddev = gfit_broad['hb_out'].stddev, name = 'hb_b')
            
            gfit_broad = g_hb_n + g_hb_out + g_hb_b
    
        #####################################################################################
        #####################################################################################

        ## Select the best-fit based on rchi2
        ## If the rchi2 of 2-component is better by 20%, then the 2-component fit is picked.
        ## Otherwise, 1-component fit is the best fit.
        del_rchi2 = ((rchi2_no_broad - rchi2_broad)/rchi2_no_broad)*100
        
        ## Further conditions -- sigma_broad > sigma_narrow
        sig_hb_n = mfit.lamspace_to_velspace(gfit_broad['hb_n'].stddev.value, \
                                             gfit_broad['hb_n'].mean.value)
        sig_hb_b = mfit.lamspace_to_velspace(gfit_broad['hb_b'].stddev.value, \
                                             gfit_broad['hb_b'].mean.value)
        
        ## Set flags
        flag_bits = np.append(flag_bits, 2)
        if (del_rchi2 >= 20):
            flag_bits = np.append(flag_bits, 4)
        if (sig_hb_b < sig_hb_n):
            flag_bits = np.append(flag_bits, 5)
        if (sig_hb_n < 40):
            flag_bits = np.append(flag_bits, 9)
        
        flag_bits = np.sort(flag_bits.astype(int))
        
        if ((del_rchi2 >= 20)&(sig_hb_b > sig_hb_n)&(sig_hb_n >= 40)):
            if (fit_cont == True):
                n_dof = 10
            else:
                n_dof = 9
            return (gfit_broad, rchi2_broad, flag_bits, n_dof)
        else:
            if (fit_cont == True):
                n_dof = 7
            else:
                n_dof = 6
            
            return (gfit_no_broad, rchi2_no_broad, flag_bits, n_dof)
    
####################################################################################################

    def fit_fixed_one_component(lam_hb, flam_hb, ivar_hb, sii_bestfit, fit_cont = True):
        """
        Function to fit Hbeta line -- fixing the width to the [SII] best-fit.
        Only for a single component - no outflow compoenent.
        The broad-component needs to be >20% better to be picked.
        
        Parameters
        ----------
        lam_hb : numpy array
            Wavelength array of the Hb region where the fits need to be performed.

        flam_hb : numpy array
            Flux array of the spectra in the Hb region.

        ivar_hb : numpy array
            Inverse variance array of the spectra in the Hb region.

        sii_bestfit : astropy model fit
            Best fit for [SII] emission lines
            Sigma of narrow Hbeta is fixed to [SII].

        Returns
        -------
        gfit : Astropy model
            Best-fit "without-broad" or "with-broad" component

        rchi2: float
            Reduced chi2 of the best-fit
            
        flag_bits : numpy array
            Array of flag bits for fixed one-component Hbeta fitting
                1 : Fixed one component fitting
                4 : chi^2 for broad-component fit improves by 20%
                5 : sigma (Hbeta broad) < sigma (Hbeta narrow)  
                
        n_dof : int
            Number of degrees of freedom
        """
        
        flag_bits = np.array([])
        
        ## Initial estimate of amplitude
        amp_hb = np.max(flam_hb)
        
        ## No outflow components
        ## Initial estimate of standard deviation
        std_hb = (4862.683/sii_bestfit['sii6716'].mean.value)*\
        sii_bestfit['sii6716'].stddev.value

        g_hb_n = Gaussian1D(amplitude = amp_hb, mean = 4862.683, \
                          stddev = std_hb, name = 'hb_n', \
                          bounds = {'amplitude' : (0.0, None), 'stddev' : (0.5, None)})

        ## Fix sigma of Hb narrow to [SII]
        def tie_std_hb(model):
            if (model.n_submodels == 1):
                return ((model.mean/sii_bestfit['sii6716'].mean)*\
                        sii_bestfit['sii6716'].stddev)
            else:
                return ((model['hb_n'].mean/sii_bestfit['sii6716'].mean)*\
                        sii_bestfit['sii6716'].stddev)

        g_hb_n.stddev.tied = tie_std_hb
        g_hb_n.stddev.fixed = True
        
        if (fit_cont == True):
        
            ## Continuum
            cont = Const1D(amplitude = 0.0, name = 'hb_cont')

            g_hb = cont + g_hb_n

            #####################################################################################
            ########################### Fit without broad component #############################

            ## Initial fit
            g_init = g_hb 
            fitter_no_broad = fitting.LevMarLSQFitter()

            gfit_no_broad = fitter_no_broad(g_init, lam_hb, flam_hb, \
                                            weights = np.sqrt(ivar_hb), maxiter = 1000)


            rchi2_no_broad = mfit.calculate_red_chi2(flam_hb, gfit_no_broad(lam_hb), \
                                                     ivar_hb, n_free_params = 3)

            #####################################################################################
            ########################### Fit with broad component ################################

            ## Two component fit
            g_hb_b = Gaussian1D(amplitude = amp_hb/4, mean = 4862.683, \
                                stddev = 4.0, name = 'hb_b', \
                                bounds = {'amplitude' : (0.0, None), 'stddev' : (1.0, None)})

            ## Initial fit
            g_init = g_hb + g_hb_b 
            fitter_broad = fitting.LevMarLSQFitter()

            gfit_broad = fitter_broad(g_init, lam_hb, flam_hb, \
                                      weights = np.sqrt(ivar_hb), maxiter = 1000)


            rchi2_broad = mfit.calculate_red_chi2(flam_hb, gfit_broad(lam_hb), \
                                                  ivar_hb, n_free_params = 6)

            #####################################################################################
            #####################################################################################
        else:

            g_hb = g_hb_n

            #####################################################################################
            ########################### Fit without broad component #############################

            ## Initial fit
            g_init = g_hb 
            fitter_no_broad = fitting.LevMarLSQFitter()

            gfit_no_broad = fitter_no_broad(g_init, lam_hb, flam_hb, \
                                            weights = np.sqrt(ivar_hb), maxiter = 1000)


            rchi2_no_broad = mfit.calculate_red_chi2(flam_hb, gfit_no_broad(lam_hb), \
                                                     ivar_hb, n_free_params = 2)

            #####################################################################################
            ########################### Fit with broad component ################################

            ## Two component fit
            g_hb_b = Gaussian1D(amplitude = amp_hb/4, mean = 4862.683, \
                                stddev = 4.0, name = 'hb_b', \
                                bounds = {'amplitude' : (0.0, None), 'stddev' : (1.0, None)})

            ## Initial fit
            g_init = g_hb + g_hb_b 
            fitter_broad = fitting.LevMarLSQFitter()

            gfit_broad = fitter_broad(g_init, lam_hb, flam_hb, \
                                      weights = np.sqrt(ivar_hb), maxiter = 1000)


            rchi2_broad = mfit.calculate_red_chi2(flam_hb, gfit_broad(lam_hb), \
                                                  ivar_hb, n_free_params = 5)

            #####################################################################################
            #####################################################################################

        ## Select the best-fit based on rchi2
        ## If the rchi2 of 2-component is better by 20%, then the 2-component fit is picked.
        ## Otherwise, 1-component fit is the best fit.
        del_rchi2 = ((rchi2_no_broad - rchi2_broad)/rchi2_no_broad)*100
        
        ## Further conditions -- sigma_broad > sigma_narrow
        sig_hb_n = mfit.lamspace_to_velspace(gfit_broad['hb_n'].stddev.value, \
                                             gfit_broad['hb_n'].mean.value)
        sig_hb_b = mfit.lamspace_to_velspace(gfit_broad['hb_b'].stddev.value, \
                                             gfit_broad['hb_b'].mean.value)
        
        ## Set flags
        flag_bits = np.append(flag_bits, 1)
        if (del_rchi2 >= 20):
            flag_bits = np.append(flag_bits, 4)
        if (sig_hb_b < sig_hb_n):
            flag_bits = np.append(flag_bits, 5)
        if (sig_hb_n < 40):
            flag_bits = np.append(flag_bits, 9)
            
        flag_bits = np.sort(flag_bits.astype(int))

        if ((del_rchi2 >= 20)&(sig_hb_b > sig_hb_n)):
            if (fit_cont == True):
                n_dof = 6
            else:
                n_dof = 5
            return (gfit_broad, rchi2_broad, flag_bits, n_dof)
        else:
            if (fit_cont == True):
                n_dof = 3
            else:
                n_dof = 2
            
            return (gfit_no_broad, rchi2_no_broad, flag_bits, n_dof)
        
####################################################################################################

    def fit_fixed_two_components(lam_hb, flam_hb, ivar_hb, sii_bestfit, fit_cont = True):
        """
        Function to fit Hbeta line -- fixing the width to the [SII] best-fit.
        Includes extra component for both Hbeta and [SII].
        The broad-component needs to be >20% better to be picked.
        
        Parameters
        ----------
        lam_hb : numpy array
            Wavelength array of the Hb region where the fits need to be performed.

        flam_hb : numpy array
            Flux array of the spectra in the Hb region.

        ivar_hb : numpy array
            Inverse variance array of the spectra in the Hb region.

        sii_bestfit : astropy model fit
            Best fit for [SII] emission lines, including outflow component.
            Sigma of narrow (outflow) Hb bounds are set to be within some percent of [SII] width.

        Returns
        -------
        gfit : Astropy model
            Best-fit "without-broad" or "with-broad" component

        rchi2: float
            Reduced chi2 of the best-fit
            
        flag_bits : numpy array
            Array of flag bits for fixed two-component Hbeta fitting
                3 : Fixed two component fitting
                4 : chi^2 for broad-component fit improves by 20%
                5 : sigma (Hbeta broad) < sigma (Hbeta narrow)
                
        n_dof : int
            Number of degrees of freedom
        """
        flag_bits = np.array([])
        
        ## Initial estimate of amplitude
        amp_hb = np.max(flam_hb)
        
        ## Initial estimate of standard deviation
        std_hb = (4862.683/sii_bestfit['sii6716'].mean.value)*\
        sii_bestfit['sii6716'].stddev.value

        std_hb_out = (4862.683/sii_bestfit['sii6716_out'].mean.value)*\
        sii_bestfit['sii6716_out'].stddev.value

        g_hb_n = Gaussian1D(amplitude = amp_hb, mean = 4862.683, \
                          stddev = std_hb, name = 'hb_n', \
                          bounds = {'amplitude' : (0.0, None), 'stddev' : (0.5, None)})

        g_hb_out = Gaussian1D(amplitude = amp_hb/3, mean = 4862.683, \
                             stddev = std_hb_out, name = 'hb_out', \
                             bounds = {'amplitude' : (0.0, None), 'stddev' : (0.5, None)})

        ## Fix sigma of narrow Hb to narrow [SII]
        def tie_std_hb(model):
            return ((model['hb_n'].mean/sii_bestfit['sii6716'].mean)*\
                    sii_bestfit['sii6716'].stddev)

        g_hb_n.stddev.tied = tie_std_hb
        g_hb_n.stddev.fixed = True

        ## Fix sigma of outflow Hb to outflow [SII]
        def tie_std_hb_out(model):
            return ((model['hb_out'].mean/sii_bestfit['sii6716_out'].mean)*\
                    sii_bestfit['sii6716_out'].stddev)

        g_hb_out.stddev.tied = tie_std_hb_out
        g_hb_out.stddev.fixed = True
        
        if (fit_cont == True):
            ## Continuum
            cont = Const1D(amplitude = 0.0, name = 'hb_cont')

            g_hb = cont + g_hb_n + g_hb_out

            #####################################################################################
            ########################### Fit without broad component #############################

            ## Initial fit
            g_init = g_hb 
            fitter_no_broad = fitting.LevMarLSQFitter()

            gfit_no_broad = fitter_no_broad(g_init, lam_hb, flam_hb, \
                                            weights = np.sqrt(ivar_hb), maxiter = 1000)

            rchi2_no_broad = mfit.calculate_red_chi2(flam_hb, gfit_no_broad(lam_hb), \
                                                         ivar_hb, n_free_params = 5)

            #####################################################################################
            ########################### Fit with broad component ################################

            ## Two component fit
            g_hb_b = Gaussian1D(amplitude = amp_hb/4, mean = 4862.683, \
                                stddev = 4.0, name = 'hb_b', \
                                bounds = {'amplitude' : (0.0, None), 'stddev' : (1.0, None)})

            ## Initial fit
            g_init = g_hb + g_hb_b 
            fitter_broad = fitting.LevMarLSQFitter()

            gfit_broad = fitter_broad(g_init, lam_hb, flam_hb, \
                                      weights = np.sqrt(ivar_hb), maxiter = 1000)


            rchi2_broad = mfit.calculate_red_chi2(flam_hb, gfit_broad(lam_hb), \
                                                  ivar_hb, n_free_params = 8)

            #####################################################################################
            #####################################################################################
        else:
            g_hb = g_hb_n + g_hb_out

            #####################################################################################
            ########################### Fit without broad component #############################

            ## Initial fit
            g_init = g_hb 
            fitter_no_broad = fitting.LevMarLSQFitter()

            gfit_no_broad = fitter_no_broad(g_init, lam_hb, flam_hb, \
                                            weights = np.sqrt(ivar_hb), maxiter = 1000)

            rchi2_no_broad = mfit.calculate_red_chi2(flam_hb, gfit_no_broad(lam_hb), \
                                                         ivar_hb, n_free_params = 4)

            #####################################################################################
            ########################### Fit with broad component ################################

            ## Two component fit
            g_hb_b = Gaussian1D(amplitude = amp_hb/4, mean = 4862.683, \
                                stddev = 4.0, name = 'hb_b', \
                                bounds = {'amplitude' : (0.0, None), 'stddev' : (1.0, None)})

            ## Initial fit
            g_init = g_hb + g_hb_b 
            fitter_broad = fitting.LevMarLSQFitter()

            gfit_broad = fitter_broad(g_init, lam_hb, flam_hb, \
                                      weights = np.sqrt(ivar_hb), maxiter = 1000)


            rchi2_broad = mfit.calculate_red_chi2(flam_hb, gfit_broad(lam_hb), \
                                                  ivar_hb, n_free_params = 7)

            #####################################################################################
            #####################################################################################

        ## Select the best-fit based on rchi2
        ## If the rchi2 of 2-component is better by 20%, then the 2-component fit is picked.
        ## Otherwise, 1-component fit is the best fit.
        del_rchi2 = ((rchi2_no_broad - rchi2_broad)/rchi2_no_broad)*100
        
        ## Further conditions -- sigma_broad > sigma_narrow
        sig_hb_n = mfit.lamspace_to_velspace(gfit_broad['hb_n'].stddev.value, \
                                             gfit_broad['hb_n'].mean.value)
        sig_hb_b = mfit.lamspace_to_velspace(gfit_broad['hb_b'].stddev.value, \
                                             gfit_broad['hb_b'].mean.value)
        
        ## Set flags
         ## Set flags
        flag_bits = np.append(flag_bits, 3)
        if (del_rchi2 >= 20):
            flag_bits = np.append(flag_bits, 4)
        if (sig_hb_b < sig_hb_n):
            flag_bits = np.append(flag_bits, 5)
        if (sig_hb_n < 40):
            flag_bits = np.append(flag_bits, 9)
        
        flag_bits = np.sort(flag_bits.astype(int))
        
        if ((del_rchi2 >= 20)&(sig_hb_b > sig_hb_n)):
            if (fit_cont == True):
                n_dof = 8
            else:
                n_dof = 7
            return (gfit_broad, rchi2_broad, flag_bits, n_dof)
        else:
            if (fit_cont == True):
                n_dof = 5
            else:
                n_dof = 4
            return (gfit_no_broad, rchi2_no_broad, flag_bits, n_dof)
        
####################################################################################################
####################################################################################################

class fit_nii_ha_lines:
    """
    Different functions associated with fitting [NII]+Ha emission-lines:
        1) fit_free_ha_one_component(lam_nii, flam_nii, ivar_nii, sii_bestfit, frac_temp, fit_cont)
        2) fit_free_ha_two_components(lam_nii, flam_nii, ivar_nii, sii_bestfit, frac_temp, fit_cont)
        3) fit_fixed_one_component(lam_nii, flam_nii, ivar_nii, sii_bestfit, fit_cont)
        4) fit_fixed_two_components(lam_nii, flam_nii, ivar_nii, sii_bestfit, fit_cont)
    """
    
    def fit_free_ha_one_component(lam_nii, flam_nii, ivar_nii, sii_bestfit, \
                                  frac_temp = 60., fit_cont = True):
        """
        Function to fit [NII]6548, 6583 emission lines.
        Sigma of [NII] is kept fixed to [SII] and
        Ha is allowed to vary within some percent (default = 60%) of [SII].
        The broad component fit needs to be >20% better to be picked.
        Code works only for one-component [SII] fits -- no outflow components.
        
        Parameters
        ----------
        lam_nii : numpy array
            Wavelength array of the [NII]+Ha region where the fits need to be performed.

        flam_nii : numpy array
            Flux array of the spectra in the [NII]+Ha region.

        ivar_nii : numpy array
            Inverse variance array of the spectra in the [NII]+Ha region.
            
        sii_bestfit : Astropy model
            Best fit model for the [SII] emission-lines.
            
        frac_temp : float
            The %age of [SII] width within which narrow Halpha width can vary
            
        Returns
        -------
        gfit : Astropy model
            Best-fit 1 component model

        rchi2: float
            Reduced chi2 of the best-fit
            
        flag_bits : numpy array
            Array of flag bits for free one-component fitting
                0 : free one component fit
                4 : chi^2 for broad-line fit improves by 20%
                5 : sigma (Ha; b) < sigma (Ha; n)
                
        n_dof : int
            Number of degrees of freedom
        """
        
        flag_bits = np.array([])
                        
        ## Initial estimate of amplitudes
        amp_nii6548 = np.max(flam_nii[(lam_nii > 6548)&(lam_nii < 6550)])
        amp_nii6583 = np.max(flam_nii[(lam_nii > 6583)&(lam_nii < 6586)])
        
        ## Initial guess of amplitude for Ha
        amp_ha = np.max(flam_nii[(lam_nii > 6550)&(lam_nii < 6575)])
        
        ## Initial estimates of standard deviation
        stddev_nii6548 = (6549.852/sii_bestfit['sii6716'].mean.value)*\
        sii_bestfit['sii6716'].stddev.value
        stddev_nii6583 = (6585.277/sii_bestfit['sii6716'].mean.value)*\
        sii_bestfit['sii6716'].stddev.value
        
        ## Two component fits
        g_nii6548 = Gaussian1D(amplitude = amp_nii6548/2, mean = 6549.852, \
                               stddev = stddev_nii6548, name = 'nii6548', \
                               bounds = {'amplitude' : (0.0, None)})
        g_nii6583 = Gaussian1D(amplitude = amp_nii6583/2, mean = 6585.277, \
                               stddev = stddev_nii6583, name = 'nii6583', \
                               bounds = {'amplitude' : (0.0, None)})

        ## Tie means of [NII] doublet gaussians
        def tie_mean_nii(model):
            return (model['nii6548'].mean + 35.425)

        g_nii6583.mean.tied = tie_mean_nii

        ## Tie amplitudes of two [NII] gaussians
        def tie_amp_nii(model):
            return (model['nii6548'].amplitude*2.96)

        g_nii6583.amplitude.tied = tie_amp_nii

        ## Tie standard deviations of all the narrow components
        def tie_std_nii6548(model):
            return ((model['nii6548'].mean/sii_bestfit['sii6716'].mean)*\
                    sii_bestfit['sii6716'].stddev)

        g_nii6548.stddev.tied = tie_std_nii6548
        g_nii6548.stddev.fixed = True

        def tie_std_nii6583(model):
            return ((model['nii6583'].mean/sii_bestfit['sii6716'].mean)*\
                    sii_bestfit['sii6716'].stddev)

        g_nii6583.stddev.tied = tie_std_nii6583
        g_nii6583.stddev.fixed = True

        g_nii = g_nii6548 + g_nii6583 
        
        ## Template fit
        temp_std = sii_bestfit['sii6716'].stddev.value
        temp_std_kms = mfit.lamspace_to_velspace(temp_std, \
                                                 sii_bestfit['sii6716'].mean.value)
        min_std_kms = temp_std_kms - ((frac_temp/100)*temp_std_kms)
        max_std_kms = temp_std_kms + ((frac_temp/100)*temp_std_kms)

        min_std_ha = mfit.velspace_to_lamspace(min_std_kms, 6564.312)
        max_std_ha = mfit.velspace_to_lamspace(max_std_kms, 6564.312)
        
        g_ha_n = Gaussian1D(amplitude = amp_ha/2, mean = 6564.312, \
                            stddev = temp_std, name = 'ha_n', \
                            bounds = {'amplitude' : (0.0, None), 'stddev' : (0.85, None)})

        ## Set narrow Ha within 60% of the template fit
        g_ha_n.stddev.bounds = (min_std_ha, max_std_ha)
        
        # Total Halpha components
        g_ha = g_ha_n
        
        if (fit_cont == True):
            ## Continuum
            cont = Const1D(amplitude = 0.0, name = 'nii_ha_cont')

            #####################################################################################
            ########################## Fit without broad component ##############################

            ## Initial gaussian fit
            g_init = cont + g_nii + g_ha

            fitter_no_broad = fitting.LevMarLSQFitter()

            gfit_no_broad = fitter_no_broad(g_init, lam_nii, flam_nii,\
                                         weights = np.sqrt(ivar_nii), maxiter = 1000)

            rchi2_no_broad = mfit.calculate_red_chi2(flam_nii, gfit_no_broad(lam_nii),\
                                                              ivar_nii, n_free_params = 6)


            #####################################################################################
            ########################## Fit with broad component #################################

            ## Broad Ha parameters
            g_ha_b = Gaussian1D(amplitude = amp_ha/5, mean = 6564.312, \
                                stddev = 6.0, name = 'ha_b', \
                                bounds = {'amplitude' : (0.0, None), 'stddev' : (1.5, None)})

            ## Initial gaussian fit
            g_init = cont + g_nii + g_ha + g_ha_b
            fitter_broad = fitting.LevMarLSQFitter()

            gfit_broad = fitter_broad(g_init, lam_nii, flam_nii,\
                                      weights = np.sqrt(ivar_nii), maxiter = 1000)


            rchi2_broad = mfit.calculate_red_chi2(flam_nii, gfit_broad(lam_nii), \
                                                           ivar_nii, n_free_params = 9)

            #####################################################################################
            #####################################################################################
        else:
            #####################################################################################
            ########################## Fit without broad component ##############################

            ## Initial gaussian fit
            g_init = g_nii + g_ha

            fitter_no_broad = fitting.LevMarLSQFitter()

            gfit_no_broad = fitter_no_broad(g_init, lam_nii, flam_nii,\
                                         weights = np.sqrt(ivar_nii), maxiter = 1000)

            rchi2_no_broad = mfit.calculate_red_chi2(flam_nii, gfit_no_broad(lam_nii),\
                                                              ivar_nii, n_free_params = 5)


            #####################################################################################
            ########################## Fit with broad component #################################

            ## Broad Ha parameters
            g_ha_b = Gaussian1D(amplitude = amp_ha/5, mean = 6564.312, \
                                stddev = 6.0, name = 'ha_b', \
                                bounds = {'amplitude' : (0.0, None), 'stddev' : (1.5, None)})

            ## Initial gaussian fit
            g_init = g_nii + g_ha + g_ha_b
            fitter_broad = fitting.LevMarLSQFitter()

            gfit_broad = fitter_broad(g_init, lam_nii, flam_nii,\
                                      weights = np.sqrt(ivar_nii), maxiter = 1000)


            rchi2_broad = mfit.calculate_red_chi2(flam_nii, gfit_broad(lam_nii), \
                                                           ivar_nii, n_free_params = 8)

            #####################################################################################
            #####################################################################################

        ## Select the best-fit based on rchi2
        ## If the rchi2 of 2-component is better by 20%, then the 2-component fit is picked.
        ## Otherwise, 1-component fit is the best fit.
        del_rchi2 = ((rchi2_no_broad - rchi2_broad)/rchi2_no_broad)*100
        
        ## Also sigma (broad Ha) > sigma (narrow Ha)
        sig_ha_b = mfit.lamspace_to_velspace(gfit_broad['ha_b'].stddev.value, \
                                             gfit_broad['ha_b'].mean.value)
        sig_ha_n = mfit.lamspace_to_velspace(gfit_broad['ha_n'].stddev.value, \
                                             gfit_broad['ha_n'].mean.value)
        
        fwhm_ha_b = 2.355*sig_ha_b
        
        ## Set flags
        flag_bits = np.append(flag_bits, 0)
        if (del_rchi2 >= 20):
            flag_bits = np.append(flag_bits, 4)
        if (sig_ha_b < sig_ha_n):
            flag_bits = np.append(flag_bits, 5)
        if (sig_ha_n < 40):
            flag_bits = np.append(flag_bits, 10)
            
        flag_bits = np.sort(flag_bits.astype(int))

        if ((del_rchi2 >= 20)&(sig_ha_b > sig_ha_n)&(sig_ha_n >= 40.)&(fwhm_ha_b >= 300.)):
            if (fit_cont == True):
                n_dof = 9
            else:
                n_dof = 8
            return (gfit_broad, rchi2_broad, flag_bits, n_dof)
        else:
            if (fit_cont == True):
                n_dof = 6
            else:
                n_dof = 5
            return (gfit_no_broad, rchi2_no_broad, flag_bits, n_dof)
        
####################################################################################################

    def fit_free_ha_two_components(lam_nii, flam_nii, ivar_nii, \
                                   sii_bestfit, frac_temp = 60., fit_cont = True):
        
        """
        Function to fit [NII]6548, 6583 emission lines.
        Sigma of [NII] is kept fixed to [SII] and
        Ha, including outflow component is allowed to 
        vary within some percent (default = 60%) of [SII].
        
        The broad component fit needs to be >20% better to be picked.
        Code works only for two-component [SII] fits, including outflow components.
        
        Parameters
        ----------
        lam_nii : numpy array
            Wavelength array of the [NII]+Ha region where the fits need to be performed.

        flam_nii : numpy array
            Flux array of the spectra in the [NII]+Ha region.

        ivar_nii : numpy array
            Inverse variance array of the spectra in the [NII]+Ha region.
            
        sii_bestfit : Astropy model
            Best fit model for the [SII] emission-lines.
            
        frac_temp : float
            The %age of [SII] width within which narrow Halpha width can vary
            
         Returns
        -------
        gfit : Astropy model
            Best-fit 2 component model

        rchi2: float
            Reduced chi2 of the best-fit
            
        flag_bits : numpy array
            Array of flag bits for fixed one-component fitting
                1 : fixed one component fit
                4 : chi^2 for broad-line fit improves by 20%
                5 : sigma (Ha; b) < sigma (Ha; n)
                6 : sigma (Ha; out) > sigma (Ha; b)
                
        n_dof : int
            Number of degrees of freedom
        """
        
        flag_bits = np.array([])
        
        ## Initial estimate of amplitudes
        amp_nii6548 = np.max(flam_nii[(lam_nii > 6548)&(lam_nii < 6550)])
        amp_nii6583 = np.max(flam_nii[(lam_nii > 6583)&(lam_nii < 6586)])
        
        ## Initial guess of amplitude for Ha
        amp_ha = np.max(flam_nii[(lam_nii > 6550)&(lam_nii < 6575)])
        
        ## Initial estimates of standard deviation
        stddev_nii6548 = (6549.852/sii_bestfit['sii6716'].mean.value)*\
        sii_bestfit['sii6716'].stddev.value
        stddev_nii6583 = (6585.277/sii_bestfit['sii6716'].mean.value)*\
        sii_bestfit['sii6716'].stddev.value

        stddev_nii6548_out = (6549.852/sii_bestfit['sii6716_out'].mean.value)*\
        sii_bestfit['sii6716_out'].stddev.value
        stddev_nii6583_out = (6585.277/sii_bestfit['sii6716_out'].mean.value)*\
        sii_bestfit['sii6716_out'].stddev.value

        ## Two component fits
        g_nii6548 = Gaussian1D(amplitude = amp_nii6548/2, mean = 6549.852, \
                               stddev = stddev_nii6548, name = 'nii6548', \
                               bounds = {'amplitude' : (0.0, None)})
        g_nii6583 = Gaussian1D(amplitude = amp_nii6583/2, mean = 6585.277, \
                               stddev = stddev_nii6583, name = 'nii6583', \
                               bounds = {'amplitude' : (0.0, None)})

        g_nii6548_out = Gaussian1D(amplitude = amp_nii6548/4, mean = 6549.852, \
                                   stddev = stddev_nii6548_out, name = 'nii6548_out', \
                                   bounds = {'amplitude' : (0.0, None)})
        g_nii6583_out = Gaussian1D(amplitude = amp_nii6583/4, mean = 6585.277, \
                                   stddev = stddev_nii6583_out, name = 'nii6583_out', \
                                   bounds = {'amplitude' : (0.0, None)})

        ## Tie means of [NII] doublet gaussians
        def tie_mean_nii(model):
            return (model['nii6548'].mean + 35.425)

        g_nii6583.mean.tied = tie_mean_nii

        ## Tie amplitudes of two [NII] gaussians
        def tie_amp_nii(model):
            return (model['nii6548'].amplitude*2.96)

        g_nii6583.amplitude.tied = tie_amp_nii

        ## Tie standard deviations of all the narrow components
        def tie_std_nii6548(model):
            return ((model['nii6548'].mean/sii_bestfit['sii6716'].mean)*\
                    sii_bestfit['sii6716'].stddev)

        g_nii6548.stddev.tied = tie_std_nii6548
        g_nii6548.stddev.fixed = True

        def tie_std_nii6583(model):
            return ((model['nii6583'].mean/sii_bestfit['sii6716'].mean)*\
                    sii_bestfit['sii6716'].stddev)

        g_nii6583.stddev.tied = tie_std_nii6583
        g_nii6583.stddev.fixed = True

        ## Tie means of [NII] outflow components
        def tie_mean_nii_out(model):
            return (model['nii6548_out'].mean + 35.425)

        g_nii6583_out.mean.tied = tie_mean_nii_out

        ## Tie amplitudes of two [NII] gaussians
        def tie_amp_nii_out(model):
            return (model['nii6548_out'].amplitude*2.96)

        g_nii6583_out.amplitude.tied = tie_amp_nii_out

        ## Tie standard deviations of all the outflow components
        def tie_std_nii6548_out(model):
            return ((model['nii6548_out'].mean/sii_bestfit['sii6716_out'].mean)*\
                    sii_bestfit['sii6716_out'].stddev)

        g_nii6548_out.stddev.tied = tie_std_nii6548_out
        g_nii6548_out.stddev.fixed = True

        def tie_std_nii6583_out(model):
            return ((model['nii6583_out'].mean/sii_bestfit['sii6716_out'].mean)*\
                    sii_bestfit['sii6716_out'].stddev)

        g_nii6583_out.stddev.tied = tie_std_nii6583_out
        g_nii6583_out.stddev.fixed = True

        g_nii = g_nii6548 + g_nii6583 + g_nii6548_out + g_nii6583_out
        
        ## Template fit
        temp_std = sii_bestfit['sii6716'].stddev.value
        temp_std_kms = mfit.lamspace_to_velspace(temp_std, \
                                                 sii_bestfit['sii6716'].mean.value)
        min_std_kms = temp_std_kms - ((frac_temp/100)*temp_std_kms)
        max_std_kms = temp_std_kms + ((frac_temp/100)*temp_std_kms)

        min_std_ha = mfit.velspace_to_lamspace(min_std_kms, 6564.312)
        max_std_ha = mfit.velspace_to_lamspace(max_std_kms, 6564.312)
        
        g_ha_n = Gaussian1D(amplitude = amp_ha/2, mean = 6564.312, \
                            stddev = temp_std, name = 'ha_n', \
                            bounds = {'amplitude' : (0.0, None), 'stddev' : (0.85, None)})

        ## Set narrow Ha within 60% of the template fit
        g_ha_n.stddev.bounds = (min_std_ha, max_std_ha)
        
        ## Outflow components
        temp_out_std = sii_bestfit['sii6716_out'].stddev.value
        temp_out_std_kms = mfit.lamspace_to_velspace(temp_out_std, \
                                                     sii_bestfit['sii6716_out'].mean.value)

        min_out_kms = temp_out_std_kms - ((frac_temp/100)*temp_out_std_kms)
        max_out_kms = temp_out_std_kms + ((frac_temp/100)*temp_out_std_kms)

        min_out = mfit.velspace_to_lamspace(min_out_kms, 6564.312)
        max_out = mfit.velspace_to_lamspace(max_out_kms, 6564.312)

        g_ha_out = Gaussian1D(amplitude = amp_ha/3, mean = 6564.312, \
                             stddev = temp_out_std, name = 'ha_out', \
                             bounds = {'amplitude': (0.0, None), 'stddev' : (0.85, None)})
        
        g_ha_out.stddev.bounds = (min_out, max_out)
        
        g_ha = g_ha_n + g_ha_out
        
        if (fit_cont == True):
            ## Continuum
            cont = Const1D(amplitude = 0.0, name = 'nii_ha_cont')

            #####################################################################################
            ########################## Fit without broad component ##############################

            ## Initial gaussian fit
            g_init = cont + g_nii + g_ha

            fitter_no_broad = fitting.LevMarLSQFitter()

            gfit_no_broad = fitter_no_broad(g_init, lam_nii, flam_nii,\
                                         weights = np.sqrt(ivar_nii), maxiter = 1000)


            rchi2_no_broad = mfit.calculate_red_chi2(flam_nii, gfit_no_broad(lam_nii),\
                                                              ivar_nii, n_free_params = 11)

            #####################################################################################
            ########################## Fit with broad component #################################

            ## Broad Ha parameters
            g_ha_b = Gaussian1D(amplitude = amp_ha/3, mean = 6564.312, \
                                stddev = 4.0, name = 'ha_b', \
                                bounds = {'amplitude' : (0.0, None), 'stddev' : (1.5, None)})

            ## Initial gaussian fit
            g_init = cont + g_nii + g_ha + g_ha_b
            fitter_broad = fitting.LevMarLSQFitter()

            gfit_broad = fitter_broad(g_init, lam_nii, flam_nii,\
                                      weights = np.sqrt(ivar_nii), maxiter = 1000)


            rchi2_broad = mfit.calculate_red_chi2(flam_nii, gfit_broad(lam_nii), \
                                                           ivar_nii, n_free_params = 14)
            #####################################################################################
            #####################################################################################
            
        else:
            #####################################################################################
            ########################## Fit without broad component ##############################

            ## Initial gaussian fit
            g_init = g_nii + g_ha

            fitter_no_broad = fitting.LevMarLSQFitter()

            gfit_no_broad = fitter_no_broad(g_init, lam_nii, flam_nii,\
                                         weights = np.sqrt(ivar_nii), maxiter = 1000)


            rchi2_no_broad = mfit.calculate_red_chi2(flam_nii, gfit_no_broad(lam_nii),\
                                                              ivar_nii, n_free_params = 10)

            #####################################################################################
            ########################## Fit with broad component #################################

            ## Broad Ha parameters
            g_ha_b = Gaussian1D(amplitude = amp_ha/3, mean = 6564.312, \
                                stddev = 4.0, name = 'ha_b', \
                                bounds = {'amplitude' : (0.0, None), 'stddev' : (1.5, None)})

            ## Initial gaussian fit
            g_init = g_nii + g_ha + g_ha_b
            fitter_broad = fitting.LevMarLSQFitter()

            gfit_broad = fitter_broad(g_init, lam_nii, flam_nii,\
                                      weights = np.sqrt(ivar_nii), maxiter = 1000)


            rchi2_broad = mfit.calculate_red_chi2(flam_nii, gfit_broad(lam_nii), \
                                                           ivar_nii, n_free_params = 13)
            
            #####################################################################################
            #####################################################################################
        
        ## If broad-sigma < outflow-sigma -- exchange the gaussians
        sigma_ha_b = mfit.lamspace_to_velspace(gfit_broad['ha_b'].stddev.value, \
                                              gfit_broad['ha_b'].mean.value)
        
        sigma_ha_out = mfit.lamspace_to_velspace(gfit_broad['ha_out'].stddev.value, \
                                                gfit_broad['ha_out'].mean.value)
        
        if (sigma_ha_b < sigma_ha_out):
            flag_bits = np.append(flag_bits, 6)
            g_ha_n = Gaussian1D(amplitude = gfit_broad['ha_n'].amplitude, \
                               mean = gfit_broad['ha_n'].mean, \
                               stddev = gfit_broad['ha_n'].stddev, name = 'ha_n')
            
            g_ha_out = Gaussian1D(amplitude = gfit_broad['ha_b'].amplitude, \
                                 mean = gfit_broad['ha_b'].mean, \
                                 stddev = gfit_broad['ha_b'].stddev, name = 'ha_out')
            
            g_ha_b = Gaussian1D(amplitude = gfit_broad['ha_out'].amplitude, \
                               mean = gfit_broad['ha_out'].mean, \
                                stddev = gfit_broad['ha_out'].stddev, name = 'ha_b')
            
            gfit_broad = g_ha_n + g_ha_out + g_ha_b

        #####################################################################################
        #####################################################################################

        ## Select the best-fit based on rchi2
        ## If the rchi2 of 2-component is better by 20%, then the 2-component fit is picked.
        ## Otherwise, 1-component fit is the best fit.
        del_rchi2 = ((rchi2_no_broad - rchi2_broad)/rchi2_no_broad)*100
        
        ## Also sigma (broad Ha) > sigma (narrow Ha)
        sig_ha_b = mfit.lamspace_to_velspace(gfit_broad['ha_b'].stddev.value, \
                                             gfit_broad['ha_b'].mean.value)
        sig_ha_n = mfit.lamspace_to_velspace(gfit_broad['ha_n'].stddev.value, \
                                             gfit_broad['ha_n'].mean.value)
        
        fwhm_ha_b = 2.355*sig_ha_b
        
        ## Set flags
        flag_bits = np.append(flag_bits, 2)
        if (del_rchi2 >= 20):
            flag_bits = np.append(flag_bits, 4)
        if (sig_ha_b < sig_ha_n):
            flag_bits = np.append(flag_bits, 5)
        if (sig_ha_n < 40):
            flag_bits = np.append(flag_bits, 10)
            
        flag_bits = np.sort(flag_bits.astype(int))

        if ((del_rchi2 >= 20)&(sig_ha_b > sig_ha_n)&(sig_ha_n >= 40.)&(fwhm_ha_b >= 300.)):
            if (fit_cont == True):
                n_dof = 14
            else:
                n_dof = 13
            return (gfit_broad, rchi2_broad, flag_bits, n_dof)
        else:
            if (fit_cont == True):
                n_dof = 11
            else:
                n_dof = 10
            return (gfit_no_broad, rchi2_no_broad, flag_bits, n_dof)

####################################################################################################
    
    def fit_fixed_one_component(lam_nii, flam_nii, ivar_nii, sii_bestfit, \
                               fit_cont = True):
        """
        Function to fit [NII]6548, 6583 emission lines.
        The code uses [SII] best fit as a template for both [NII] and Ha.
        The broad component fit needs to be >20% better to be picked.
        Code works only for single-component [SII] fits. No outflow components.
        
        Parameters
        ----------
        lam_nii : numpy array
            Wavelength array of the [NII]+Ha region where the fits need to be performed.

        flam_nii : numpy array
            Flux array of the spectra in the [NII]+Ha region.

        ivar_nii : numpy array
            Inverse variance array of the spectra in the [NII]+Ha region.
            
        sii_bestfit : Astropy model
            Best fit model for the [SII] emission-lines.
            
        Returns
        -------
        gfit : Astropy model
            Best-fit 1 component model

        rchi2: float
            Reduced chi2 of the best-fit
            
        flag_bits : numpy array
            Array of flag bits for free one-component fitting
                2 : free two component fit
                4 : chi^2 for broad-line fit improves by 20%
                5 : sigma (Ha; b) < sigma (Ha; n)
                
        n_dof : int
            Number of degrees of freedom
        """
        
        flag_bits = np.array([])
        
        ## Initial estimate of amplitudes
        amp_nii6548 = np.max(flam_nii[(lam_nii > 6548)&(lam_nii < 6550)])
        amp_nii6583 = np.max(flam_nii[(lam_nii > 6583)&(lam_nii < 6586)])
        
        ## Initial guess of amplitude for Ha
        amp_ha = np.max(flam_nii[(lam_nii > 6550)&(lam_nii < 6575)])
        
        ## Initial estimates of standard deviation
        stddev_nii6548 = (6549.852/sii_bestfit['sii6716'].mean.value)*\
        sii_bestfit['sii6716'].stddev.value
        stddev_nii6583 = (6585.277/sii_bestfit['sii6716'].mean.value)*\
        sii_bestfit['sii6716'].stddev.value

        ## Single component fits
        g_nii6548 = Gaussian1D(amplitude = amp_nii6548, mean = 6549.852, \
                               stddev = stddev_nii6548, name = 'nii6548', \
                               bounds = {'amplitude' : (0.0, None)})
        g_nii6583 = Gaussian1D(amplitude = amp_nii6583, mean = 6585.277, \
                               stddev = stddev_nii6583, name = 'nii6583', \
                               bounds = {'amplitude' : (0.0, None)})

        ## Tie means of [NII] doublet gaussians
        def tie_mean_nii(model):
            return (model['nii6548'].mean + 35.425)

        g_nii6583.mean.tied = tie_mean_nii

        ## Tie amplitudes of two [NII] gaussians
        def tie_amp_nii(model):
            return (model['nii6548'].amplitude*2.96)

        g_nii6583.amplitude.tied = tie_amp_nii

        ## Tie standard deviations of all the narrow components
        def tie_std_nii6548(model):
            return ((model['nii6548'].mean/sii_bestfit['sii6716'].mean)*\
                    sii_bestfit['sii6716'].stddev)

        g_nii6548.stddev.tied = tie_std_nii6548
        g_nii6548.stddev.fixed = True

        def tie_std_nii6583(model):
            return ((model['nii6583'].mean/sii_bestfit['sii6716'].mean)*\
                    sii_bestfit['sii6716'].stddev)

        g_nii6583.stddev.tied = tie_std_nii6583
        g_nii6583.stddev.fixed = True

        g_nii = g_nii6548 + g_nii6583

        ## Ha parameters
        ## Model narrow Ha as narrow [SII]
        stddev_ha = (6564.312/sii_bestfit['sii6716'].mean.value)*\
        sii_bestfit['sii6716'].stddev.value

        g_ha_n = Gaussian1D(amplitude = amp_ha/2, mean = 6564.312, \
                            stddev = stddev_ha, name = 'ha_n', \
                            bounds = {'amplitude' : (0.0, None), 'stddev' : (0.85, None)})

        ## Tie standard deviation of Ha
        def tie_std_ha(model):
            return ((model['ha_n'].mean/sii_bestfit['sii6716'].mean)*\
                    sii_bestfit['sii6716'].stddev)

        g_ha_n.stddev.tied = tie_std_ha
        g_ha_n.stddev.fixed = True

        g_ha = g_ha_n
        
        if (fit_cont == True):
            ## Continuum
            cont = Const1D(amplitude = 0.0, name = 'nii_ha_cont')

            #####################################################################################
            ########################## Fit without broad component ##############################

            ## Initial gaussian fit
            g_init = cont + g_nii + g_ha

            fitter_no_broad = fitting.LevMarLSQFitter()

            gfit_no_broad = fitter_no_broad(g_init, lam_nii, flam_nii,\
                                         weights = np.sqrt(ivar_nii), maxiter = 1000)


            rchi2_no_broad = mfit.calculate_red_chi2(flam_nii, gfit_no_broad(lam_nii),\
                                                              ivar_nii, n_free_params = 5)


            #####################################################################################
            ########################## Fit with broad component #################################

            ## Broad Ha parameters
            g_ha_b = Gaussian1D(amplitude = amp_ha/5, mean = 6564.312, \
                                stddev = 6.0, name = 'ha_b', \
                                bounds = {'amplitude' : (0.0, None), 'stddev' : (1.5, None)})

            ## Initial gaussian fit
            g_init = cont + g_nii + g_ha + g_ha_b
            fitter_broad = fitting.LevMarLSQFitter()

            gfit_broad = fitter_broad(g_init, lam_nii, flam_nii,\
                                      weights = np.sqrt(ivar_nii), maxiter = 1000)


            rchi2_broad = mfit.calculate_red_chi2(flam_nii, gfit_broad(lam_nii), \
                                                           ivar_nii, n_free_params = 8)

            #####################################################################################
            #####################################################################################
            
        else:

            #####################################################################################
            ########################## Fit without broad component ##############################

            ## Initial gaussian fit
            g_init = g_nii + g_ha

            fitter_no_broad = fitting.LevMarLSQFitter()

            gfit_no_broad = fitter_no_broad(g_init, lam_nii, flam_nii,\
                                         weights = np.sqrt(ivar_nii), maxiter = 1000)


            rchi2_no_broad = mfit.calculate_red_chi2(flam_nii, gfit_no_broad(lam_nii),\
                                                              ivar_nii, n_free_params = 4)


            #####################################################################################
            ########################## Fit with broad component #################################

            ## Broad Ha parameters
            g_ha_b = Gaussian1D(amplitude = amp_ha/5, mean = 6564.312, \
                                stddev = 6.0, name = 'ha_b', \
                                bounds = {'amplitude' : (0.0, None), 'stddev' : (1.5, None)})

            ## Initial gaussian fit
            g_init = g_nii + g_ha + g_ha_b
            fitter_broad = fitting.LevMarLSQFitter()

            gfit_broad = fitter_broad(g_init, lam_nii, flam_nii,\
                                      weights = np.sqrt(ivar_nii), maxiter = 1000)


            rchi2_broad = mfit.calculate_red_chi2(flam_nii, gfit_broad(lam_nii), \
                                                           ivar_nii, n_free_params = 7)

            #####################################################################################
            #####################################################################################

        ## Select the best-fit based on rchi2
        ## If the rchi2 of 2-component is better by 20%, then the 2-component fit is picked.
        ## Otherwise, 1-component fit is the best fit.
        del_rchi2 = ((rchi2_no_broad - rchi2_broad)/rchi2_no_broad)*100
        
        ## Also sigma (broad Ha) > sigma (narrow Ha)
        sig_ha_b = mfit.lamspace_to_velspace(gfit_broad['ha_b'].stddev.value, \
                                             gfit_broad['ha_b'].mean.value)
        sig_ha_n = mfit.lamspace_to_velspace(gfit_broad['ha_n'].stddev.value, \
                                             gfit_broad['ha_n'].mean.value)
        
        fwhm_ha_b = 2.355*sig_ha_b
        
        ## Set flags
        flag_bits = np.append(flag_bits, 1)
        if (del_rchi2 >= 20):
            flag_bits = np.append(flag_bits, 4)
        if (sig_ha_b < sig_ha_n):
            flag_bits = np.append(flag_bits, 5)
        if (sig_ha_n < 40):
            flag_bits = np.append(flag_bits, 10)
            
        flag_bits = np.sort(flag_bits.astype(int))

        if ((del_rchi2 >= 20)&(sig_ha_b > sig_ha_n)&(fwhm_ha_b >= 300.)):
            if (fit_cont == True):
                n_dof = 8
            else:
                n_dof = 7
            return (gfit_broad, rchi2_broad, flag_bits, n_dof)
        else:
            if (fit_cont == True):
                n_dof = 5
            else:
                n_dof = 4
            
            return (gfit_no_broad, rchi2_no_broad, flag_bits, n_dof)
        
####################################################################################################

    def fit_fixed_two_components(lam_nii, flam_nii, ivar_nii, sii_bestfit, \
                                fit_cont = True):
        """
        Function to fit [NII]6548, 6583 emission lines.
        The code uses [SII] best fit as a template for both [NII] and Ha.
        The broad component fit needs to be >20% better to be picked.
        Code works only for two-component [SII] fits, including outflow components.
        
        Parameters
        ----------
        lam_nii : numpy array
            Wavelength array of the [NII]+Ha region where the fits need to be performed.

        flam_nii : numpy array
            Flux array of the spectra in the [NII]+Ha region.

        ivar_nii : numpy array
            Inverse variance array of the spectra in the [NII]+Ha region.
            
        sii_bestfit : Astropy model
            Best fit model for the [SII] emission-lines.
            
         Returns
        -------
        gfit : Astropy model
            Best-fit 1 component model

        rchi2: float
            Reduced chi2 of the best-fit
            
        flag_bits : numpy array
            Array of flag bits for fixed two-component fitting
                3 : fixed one component fit
                4 : chi^2 for broad-line fit improves by 20%
                5 : sigma (Ha; b) < sigma (Ha; n)
                
        n_dof : int
            Number of degrees of freedom
        """
        
        flag_bits = np.array([])
        
        ## Initial estimate of amplitudes
        amp_nii6548 = np.max(flam_nii[(lam_nii > 6548)&(lam_nii < 6550)])
        amp_nii6583 = np.max(flam_nii[(lam_nii > 6583)&(lam_nii < 6586)])
        
        ## Initial guess of amplitude for Ha
        amp_ha = np.max(flam_nii[(lam_nii > 6550)&(lam_nii < 6575)])
        
        ## Initial estimates of standard deviation
        stddev_nii6548 = (6549.852/sii_bestfit['sii6716'].mean.value)*\
        sii_bestfit['sii6716'].stddev.value
        stddev_nii6583 = (6585.277/sii_bestfit['sii6716'].mean.value)*\
        sii_bestfit['sii6716'].stddev.value
        
        stddev_nii6548_out = (6549.852/sii_bestfit['sii6716_out'].mean.value)*\
        sii_bestfit['sii6716_out'].stddev.value
        stddev_nii6583_out = (6585.277/sii_bestfit['sii6716_out'].mean.value)*\
        sii_bestfit['sii6716_out'].stddev.value

        ## Two component fits
        g_nii6548 = Gaussian1D(amplitude = amp_nii6548/2, mean = 6549.852, \
                               stddev = stddev_nii6548, name = 'nii6548', \
                               bounds = {'amplitude' : (0.0, None)})
        g_nii6583 = Gaussian1D(amplitude = amp_nii6583/2, mean = 6585.277, \
                               stddev = stddev_nii6583, name = 'nii6583', \
                               bounds = {'amplitude' : (0.0, None)})

        g_nii6548_out = Gaussian1D(amplitude = amp_nii6548/4, mean = 6549.852, \
                                   stddev = stddev_nii6548_out, name = 'nii6548_out', \
                                   bounds = {'amplitude' : (0.0, None)})
        g_nii6583_out = Gaussian1D(amplitude = amp_nii6583/4, mean = 6585.277, \
                                   stddev = stddev_nii6583_out, name = 'nii6583_out', \
                                   bounds = {'amplitude' : (0.0, None)})

        ## Tie means of [NII] doublet gaussians
        def tie_mean_nii(model):
            return (model['nii6548'].mean + 35.425)

        g_nii6583.mean.tied = tie_mean_nii

        ## Tie amplitudes of two [NII] gaussians
        def tie_amp_nii(model):
            return (model['nii6548'].amplitude*2.96)

        g_nii6583.amplitude.tied = tie_amp_nii

        ## Tie standard deviations of all the narrow components
        def tie_std_nii6548(model):
            return ((model['nii6548'].mean/sii_bestfit['sii6716'].mean)*\
                    sii_bestfit['sii6716'].stddev)

        g_nii6548.stddev.tied = tie_std_nii6548
        g_nii6548.stddev.fixed = True

        def tie_std_nii6583(model):
            return ((model['nii6583'].mean/sii_bestfit['sii6716'].mean)*\
                    sii_bestfit['sii6716'].stddev)

        g_nii6583.stddev.tied = tie_std_nii6583
        g_nii6583.stddev.fixed = True

        ## Tie means of [NII] outflow components
        def tie_mean_nii_out(model):
            return (model['nii6548_out'].mean + 35.425)

        g_nii6583_out.mean.tied = tie_mean_nii_out

        ## Tie amplitudes of two [NII] gaussians
        def tie_amp_nii_out(model):
            return (model['nii6548_out'].amplitude*2.96)

        g_nii6583_out.amplitude.tied = tie_amp_nii_out

        ## Tie standard deviations of all the outflow components
        def tie_std_nii6548_out(model):
            return ((model['nii6548_out'].mean/sii_bestfit['sii6716_out'].mean)*\
                    sii_bestfit['sii6716_out'].stddev)

        g_nii6548_out.stddev.tied = tie_std_nii6548_out
        g_nii6548_out.stddev.fixed = True

        def tie_std_nii6583_out(model):
            return ((model['nii6583_out'].mean/sii_bestfit['sii6716_out'].mean)*\
                    sii_bestfit['sii6716_out'].stddev)

        g_nii6583_out.stddev.tied = tie_std_nii6583_out
        g_nii6583_out.stddev.fixed = True

        g_nii = g_nii6548 + g_nii6583 + g_nii6548_out + g_nii6583_out

        ### Halpha Parameters ##

        ## Ha parameters
        ## Model narrow Ha as narrow [SII]
        stddev_ha = (6564.312/sii_bestfit['sii6716'].mean.value)*\
        sii_bestfit['sii6716'].stddev.value
        ## Model outflow Ha as outflow [SII]
        stddev_ha_out = (6564.312/sii_bestfit['sii6716_out'].mean.value)*\
        sii_bestfit['sii6716_out'].stddev.value

        g_ha_n = Gaussian1D(amplitude = amp_ha/2, mean = 6564.312, \
                            stddev = stddev_ha, name = 'ha_n', \
                            bounds = {'amplitude' : (0.0, None), 'stddev' : (0.85, None)})

        g_ha_out = Gaussian1D(amplitude = amp_ha/3, mean = 6564.312, \
                              stddev = stddev_ha_out, name = 'ha_out', \
                              bounds = {'amplitude' : (0.0, None), 'stddev' : (0.85, None)})

        ## Tie standard deviation of Ha
        def tie_std_ha(model):
            return ((model['ha_n'].mean/sii_bestfit['sii6716'].mean)*\
                    sii_bestfit['sii6716'].stddev)

        g_ha_n.stddev.tied = tie_std_ha
        g_ha_n.stddev.fixed = True

        ## Tie standard deviation of Ha outflow
        def tie_std_ha_out(model):
            return ((model['ha_out'].mean/sii_bestfit['sii6716_out'].mean)*\
                    sii_bestfit['sii6716_out'].stddev)

        g_ha_out.stddev.tied = tie_std_ha_out
        g_ha_out.stddev.fixed = True

        g_ha = g_ha_n + g_ha_out
        
        if (fit_cont == True):
            ## Continuum
            cont = Const1D(amplitude = 0.0, name = 'nii_ha_cont')

            #####################################################################################
            ########################## Fit without broad component ##############################

            ## Initial gaussian fit
            g_init = cont + g_nii + g_ha

            fitter_no_broad = fitting.LevMarLSQFitter()

            gfit_no_broad = fitter_no_broad(g_init, lam_nii, flam_nii,\
                                         weights = np.sqrt(ivar_nii), maxiter = 1000)


            rchi2_no_broad = mfit.calculate_red_chi2(flam_nii, gfit_no_broad(lam_nii),\
                                                              ivar_nii, n_free_params = 9)

            #####################################################################################
            ########################## Fit with broad component #################################

            ## Broad Ha parameters
            g_ha_b = Gaussian1D(amplitude = amp_ha/3, mean = 6564.312, \
                                stddev = 4.0, name = 'ha_b', \
                                bounds = {'amplitude' : (0.0, None), 'stddev' : (1.5, None)})

            ## Initial gaussian fit
            g_init = cont + g_nii + g_ha + g_ha_b
            fitter_broad = fitting.LevMarLSQFitter()

            gfit_broad = fitter_broad(g_init, lam_nii, flam_nii,\
                                      weights = np.sqrt(ivar_nii), maxiter = 1000)


            rchi2_broad = mfit.calculate_red_chi2(flam_nii, gfit_broad(lam_nii), \
                                                           ivar_nii, n_free_params = 12)

            #####################################################################################
            #####################################################################################
            
        else:

            #####################################################################################
            ########################## Fit without broad component ##############################

            ## Initial gaussian fit
            g_init = g_nii + g_ha

            fitter_no_broad = fitting.LevMarLSQFitter()

            gfit_no_broad = fitter_no_broad(g_init, lam_nii, flam_nii,\
                                         weights = np.sqrt(ivar_nii), maxiter = 1000)


            rchi2_no_broad = mfit.calculate_red_chi2(flam_nii, gfit_no_broad(lam_nii),\
                                                              ivar_nii, n_free_params = 8)

            #####################################################################################
            ########################## Fit with broad component #################################

            ## Broad Ha parameters
            g_ha_b = Gaussian1D(amplitude = amp_ha/3, mean = 6564.312, \
                                stddev = 4.0, name = 'ha_b', \
                                bounds = {'amplitude' : (0.0, None), 'stddev' : (1.5, None)})

            ## Initial gaussian fit
            g_init = g_nii + g_ha + g_ha_b
            fitter_broad = fitting.LevMarLSQFitter()

            gfit_broad = fitter_broad(g_init, lam_nii, flam_nii,\
                                      weights = np.sqrt(ivar_nii), maxiter = 1000)


            rchi2_broad = mfit.calculate_red_chi2(flam_nii, gfit_broad(lam_nii), \
                                                           ivar_nii, n_free_params = 11)

            #####################################################################################
            #####################################################################################

        ## Select the best-fit based on rchi2
        ## If the rchi2 of 2-component is better by 20%, then the 2-component fit is picked.
        ## Otherwise, 1-component fit is the best fit.
        del_rchi2 = ((rchi2_no_broad - rchi2_broad)/rchi2_no_broad)*100
        
        ## Also sigma (broad Ha) > sigma (narrow Ha)
        sig_ha_b = mfit.lamspace_to_velspace(gfit_broad['ha_b'].stddev.value, \
                                             gfit_broad['ha_b'].mean.value)
        sig_ha_n = mfit.lamspace_to_velspace(gfit_broad['ha_n'].stddev.value, \
                                             gfit_broad['ha_n'].mean.value)
        
        fwhm_ha_b = 2.355*sig_ha_b
        
        ## Set flags
        flag_bits = np.append(flag_bits, 3)
        if (del_rchi2 >= 20):
            flag_bits = np.append(flag_bits, 4)
        if (sig_ha_b < sig_ha_n):
            flag_bits = np.append(flag_bits, 5)
        if (sig_ha_n < 40):
            flag_bits = np.append(flag_bits, 10)
            
        flag_bits = np.sort(flag_bits.astype(int))

        if ((del_rchi2 >= 20)&(sig_ha_b > sig_ha_n)&(fwhm_ha_b >= 300.)):
            if (fit_cont == True):
                n_dof = 12
            else:
                n_dof = 11
            return (gfit_broad, rchi2_broad, flag_bits, n_dof)
        else:
            if (fit_cont == True):
                n_dof = 9
            else:
                n_dof = 8
            
            return (gfit_no_broad, rchi2_no_broad, flag_bits, n_dof)
        
####################################################################################################
####################################################################################################

# class fit_nii_ha_lines_v2:
#     """
#     Different functions associated with fitting [NII]+Ha emission-lines:
#         1) fit_free_ha_one_component(lam_nii, flam_nii, ivar_nii, sii_bestfit, frac_temp)
#         2) fit_free_ha_two_components(lam_nii, flam_nii, ivar_nii, sii_bestfit, frac_temp)
#         3) fit_fixed_one_component(lam_nii, flam_nii, ivar_nii, sii_bestfit)
#         4) fit_fixed_two_components(lam_nii, flam_nii, ivar_nii, sii_bestfit)
#     """
    
#     def fit_free_ha_one_component(lam_nii, flam_nii, ivar_nii, sii_bestfit, frac_temp = 60.):
#         """
#         Function to fit [NII]6548, 6583 emission lines.
#         Sigma of [NII] is kept fixed to [SII] and
#         Ha is allowed to vary within some percent (default = 60%) of [SII].
#         The broad component fit needs to be >20% better to be picked.
#         Code works only for one-component [SII] fits -- no outflow components.
        
#         Parameters
#         ----------
#         lam_nii : numpy array
#             Wavelength array of the [NII]+Ha region where the fits need to be performed.
#         flam_nii : numpy array
#             Flux array of the spectra in the [NII]+Ha region.
#         ivar_nii : numpy array
#             Inverse variance array of the spectra in the [NII]+Ha region.
            
#         sii_bestfit : Astropy model
#             Best fit model for the [SII] emission-lines.
            
#         frac_temp : float
#             The %age of [SII] width within which narrow Halpha width can vary
            
#         Returns
#         -------
#         gfit : Astropy model
#             Best-fit 1 component model
#         rchi2: float
#             Reduced chi2 of the best-fit
            
#         flag_bits : numpy array
#             Array of flag bits for free one-component fitting
#                 0 : free one component fit
#                 4 : chi^2 for broad-line fit improves by 20%
#                 5 : sigma (Ha; b) < sigma (Ha; n)
                
#         del_rchi2 : float
#             Percentage difference between rchi2 with and without broad-line.
#         """
        
#         flag_bits = np.array([])
                        
#         ## Initial estimate of amplitudes
#         amp_nii6548 = np.max(flam_nii[(lam_nii > 6548)&(lam_nii < 6550)])
#         amp_nii6583 = np.max(flam_nii[(lam_nii > 6583)&(lam_nii < 6586)])
        
#         ## Initial guess of amplitude for Ha
#         amp_ha = np.max(flam_nii[(lam_nii > 6550)&(lam_nii < 6575)])
        
#         ## Initial estimates of standard deviation
#         stddev_nii6548 = (6549.852/sii_bestfit['sii6716'].mean.value)*\
#         sii_bestfit['sii6716'].stddev.value
#         stddev_nii6583 = (6585.277/sii_bestfit['sii6716'].mean.value)*\
#         sii_bestfit['sii6716'].stddev.value
        
#         ## Two component fits
#         g_nii6548 = Gaussian1D(amplitude = amp_nii6548/2, mean = 6549.852, \
#                                stddev = stddev_nii6548, name = 'nii6548', \
#                                bounds = {'amplitude' : (0.0, None)})
#         g_nii6583 = Gaussian1D(amplitude = amp_nii6583/2, mean = 6585.277, \
#                                stddev = stddev_nii6583, name = 'nii6583', \
#                                bounds = {'amplitude' : (0.0, None)})

#         ## Tie means of [NII] doublet gaussians
#         def tie_mean_nii(model):
#             return (model['nii6548'].mean + 35.425)

#         g_nii6583.mean.tied = tie_mean_nii

#         ## Tie amplitudes of two [NII] gaussians
#         def tie_amp_nii(model):
#             return (model['nii6548'].amplitude*2.96)

#         g_nii6583.amplitude.tied = tie_amp_nii

#         ## Tie standard deviations of all the narrow components
#         def tie_std_nii6548(model):
#             return ((model['nii6548'].mean/sii_bestfit['sii6716'].mean)*\
#                     sii_bestfit['sii6716'].stddev)

#         g_nii6548.stddev.tied = tie_std_nii6548
#         g_nii6548.stddev.fixed = True

#         def tie_std_nii6583(model):
#             return ((model['nii6583'].mean/sii_bestfit['sii6716'].mean)*\
#                     sii_bestfit['sii6716'].stddev)

#         g_nii6583.stddev.tied = tie_std_nii6583
#         g_nii6583.stddev.fixed = True

#         g_nii = g_nii6548 + g_nii6583 
        
#         ## Template fit
#         temp_std = sii_bestfit['sii6716'].stddev.value
#         temp_std_kms = mfit.lamspace_to_velspace(temp_std, \
#                                                  sii_bestfit['sii6716'].mean.value)
#         min_std_kms = temp_std_kms - ((frac_temp/100)*temp_std_kms)
#         max_std_kms = temp_std_kms + ((frac_temp/100)*temp_std_kms)

#         min_std_ha = mfit.velspace_to_lamspace(min_std_kms, 6564.312)
#         max_std_ha = mfit.velspace_to_lamspace(max_std_kms, 6564.312)
        
#         g_ha_n = Gaussian1D(amplitude = amp_ha, mean = 6564.312, \
#                             stddev = temp_std, name = 'ha_n', \
#                             bounds = {'amplitude' : (0.0, None), 'stddev' : (0.85, None)})

#         ## Set narrow Ha within 60% of the template fit
#         g_ha_n.stddev.bounds = (min_std_ha, max_std_ha)
        
#         # Total Halpha components
#         g_ha = g_ha_n
        
#         ## Continuum
#         cont = Const1D(amplitude = 0.0, name = 'nii_ha_cont')
        
#         #####################################################################################
#         ########################## Fit without broad component ##############################

#         ## Initial gaussian fit
#         g_init = cont + g_nii + g_ha

#         fitter_no_broad = fitting.LevMarLSQFitter()

#         gfit_no_broad = fitter_no_broad(g_init, lam_nii, flam_nii,\
#                                      weights = np.sqrt(ivar_nii), maxiter = 1000)

        
#         rchi2_no_broad = mfit.calculate_red_chi2(flam_nii, gfit_no_broad(lam_nii),\
#                                                           ivar_nii, n_free_params = 6)
        

#         #####################################################################################
#         ########################## Fit with broad component #################################

#         ## Broad Ha parameters
#         g_ha_b = Gaussian1D(amplitude = amp_ha/3, mean = 6564.312, \
#                             stddev = 4.0, name = 'ha_b', \
#                             bounds = {'amplitude' : (0.0, None), 'stddev' : (1.5, None)})

#         ## Initial gaussian fit
#         g_init = cont + g_nii + g_ha + g_ha_b
#         fitter_broad = fitting.LevMarLSQFitter()

#         gfit_broad = fitter_broad(g_init, lam_nii, flam_nii,\
#                                   weights = np.sqrt(ivar_nii), maxiter = 1000)

        
#         rchi2_broad = mfit.calculate_red_chi2(flam_nii, gfit_broad(lam_nii), \
#                                                        ivar_nii, n_free_params = 9)

#         #####################################################################################
#         #####################################################################################

#         ## Select the best-fit based on rchi2
#         ## If the rchi2 of 2-component is better by 20%, then the 2-component fit is picked.
#         ## Otherwise, 1-component fit is the best fit.
#         del_rchi2 = ((rchi2_no_broad - rchi2_broad)/rchi2_no_broad)*100
        
#         ## Also sigma (broad Ha) > sigma (narrow Ha)
#         sig_ha_b = mfit.lamspace_to_velspace(gfit_broad['ha_b'].stddev.value, \
#                                              gfit_broad['ha_b'].mean.value)
#         sig_ha_n = mfit.lamspace_to_velspace(gfit_broad['ha_n'].stddev.value, \
#                                              gfit_broad['ha_n'].mean.value)
        
#         fwhm_ha_b = 2.355*sig_ha_b
        
#         ## Set flags
#         flag_bits = np.append(flag_bits, 0)
#         if (del_rchi2 >= 20):
#             flag_bits = np.append(flag_bits, 4)
#         if (sig_ha_b < sig_ha_n):
#             flag_bits = np.append(flag_bits, 5)
#         if (sig_ha_n < 40):
#             flag_bits = np.append(flag_bits, 10)
            
#         flag_bits = np.sort(flag_bits.astype(int))

#         if ((del_rchi2 >= 20)&(sig_ha_b > sig_ha_n)&(sig_ha_n >= 40.)&(fwhm_ha_b >= 300.)):
#             return (gfit_broad, rchi2_broad, flag_bits, del_rchi2)
#         else:
#             return (gfit_no_broad, rchi2_no_broad, flag_bits, del_rchi2)
        
# ####################################################################################################

#     def fit_free_ha_two_components(lam_nii, flam_nii, ivar_nii, \
#                                              sii_bestfit, frac_temp = 60.):
        
#         """
#         Function to fit [NII]6548, 6583 emission lines.
#         Sigma of [NII] is kept fixed to [SII] and
#         Ha, including outflow component is allowed to 
#         vary within some percent (default = 60%) of [SII].
        
#         The broad component fit needs to be >20% better to be picked.
#         Code works only for two-component [SII] fits, including outflow components.
        
#         Parameters
#         ----------
#         lam_nii : numpy array
#             Wavelength array of the [NII]+Ha region where the fits need to be performed.
#         flam_nii : numpy array
#             Flux array of the spectra in the [NII]+Ha region.
#         ivar_nii : numpy array
#             Inverse variance array of the spectra in the [NII]+Ha region.
            
#         sii_bestfit : Astropy model
#             Best fit model for the [SII] emission-lines.
            
#         frac_temp : float
#             The %age of [SII] width within which narrow Halpha width can vary
            
#          Returns
#         -------
#         gfit : Astropy model
#             Best-fit 2 component model
#         rchi2: float
#             Reduced chi2 of the best-fit
            
#         flag_bits : numpy array
#             Array of flag bits for fixed one-component fitting
#                 1 : fixed one component fit
#                 4 : chi^2 for broad-line fit improves by 20%
#                 5 : sigma (Ha; b) < sigma (Ha; n)
#                 6 : sigma (Ha; out) > sigma (Ha; b)
                
#         del_rchi2 : float
#             Percentage difference between rchi2 with and without broad-line.
#         """
        
#         flag_bits = np.array([])
        
#         ## Initial estimate of amplitudes
#         amp_nii6548 = np.max(flam_nii[(lam_nii > 6548)&(lam_nii < 6550)])
#         amp_nii6583 = np.max(flam_nii[(lam_nii > 6583)&(lam_nii < 6586)])
        
#         ## Initial guess of amplitude for Ha
#         amp_ha = np.max(flam_nii[(lam_nii > 6550)&(lam_nii < 6575)])
        
#         ## Initial estimates of standard deviation
#         stddev_nii6548 = (6549.852/sii_bestfit['sii6716'].mean.value)*\
#         sii_bestfit['sii6716'].stddev.value
#         stddev_nii6583 = (6585.277/sii_bestfit['sii6716'].mean.value)*\
#         sii_bestfit['sii6716'].stddev.value

#         stddev_nii6548_out = (6549.852/sii_bestfit['sii6716_out'].mean.value)*\
#         sii_bestfit['sii6716_out'].stddev.value
#         stddev_nii6583_out = (6585.277/sii_bestfit['sii6716_out'].mean.value)*\
#         sii_bestfit['sii6716_out'].stddev.value

#         ## Two component fits
#         g_nii6548 = Gaussian1D(amplitude = amp_nii6548/2, mean = 6549.852, \
#                                stddev = stddev_nii6548, name = 'nii6548', \
#                                bounds = {'amplitude' : (0.0, None)})
#         g_nii6583 = Gaussian1D(amplitude = amp_nii6583/2, mean = 6585.277, \
#                                stddev = stddev_nii6583, name = 'nii6583', \
#                                bounds = {'amplitude' : (0.0, None)})

#         g_nii6548_out = Gaussian1D(amplitude = amp_nii6548/4, mean = 6549.852, \
#                                    stddev = stddev_nii6548_out, name = 'nii6548_out', \
#                                    bounds = {'amplitude' : (0.0, None)})
#         g_nii6583_out = Gaussian1D(amplitude = amp_nii6583/4, mean = 6585.277, \
#                                    stddev = stddev_nii6583_out, name = 'nii6583_out', \
#                                    bounds = {'amplitude' : (0.0, None)})

#         ## Tie means of [NII] doublet gaussians
#         def tie_mean_nii(model):
#             return (model['nii6548'].mean + 35.425)

#         g_nii6583.mean.tied = tie_mean_nii

#         ## Tie amplitudes of two [NII] gaussians
#         def tie_amp_nii(model):
#             return (model['nii6548'].amplitude*2.96)

#         g_nii6583.amplitude.tied = tie_amp_nii

#         ## Tie standard deviations of all the narrow components
#         def tie_std_nii6548(model):
#             return ((model['nii6548'].mean/sii_bestfit['sii6716'].mean)*\
#                     sii_bestfit['sii6716'].stddev)

#         g_nii6548.stddev.tied = tie_std_nii6548
#         g_nii6548.stddev.fixed = True

#         def tie_std_nii6583(model):
#             return ((model['nii6583'].mean/sii_bestfit['sii6716'].mean)*\
#                     sii_bestfit['sii6716'].stddev)

#         g_nii6583.stddev.tied = tie_std_nii6583
#         g_nii6583.stddev.fixed = True

#         ## Tie means of [NII] outflow components
#         def tie_mean_nii_out(model):
#             return (model['nii6548_out'].mean + 35.425)

#         g_nii6583_out.mean.tied = tie_mean_nii_out

#         ## Tie amplitudes of two [NII] gaussians
#         def tie_amp_nii_out(model):
#             return (model['nii6548_out'].amplitude*2.96)

#         g_nii6583_out.amplitude.tied = tie_amp_nii_out

#         ## Tie standard deviations of all the outflow components
#         def tie_std_nii6548_out(model):
#             return ((model['nii6548_out'].mean/sii_bestfit['sii6716_out'].mean)*\
#                     sii_bestfit['sii6716_out'].stddev)

#         g_nii6548_out.stddev.tied = tie_std_nii6548_out
#         g_nii6548_out.stddev.fixed = True

#         def tie_std_nii6583_out(model):
#             return ((model['nii6583_out'].mean/sii_bestfit['sii6716_out'].mean)*\
#                     sii_bestfit['sii6716_out'].stddev)

#         g_nii6583_out.stddev.tied = tie_std_nii6583_out
#         g_nii6583_out.stddev.fixed = True

#         g_nii = g_nii6548 + g_nii6583 + g_nii6548_out + g_nii6583_out
        
#         ## Template fit
#         temp_std = sii_bestfit['sii6716'].stddev.value
#         temp_std_kms = mfit.lamspace_to_velspace(temp_std, \
#                                                  sii_bestfit['sii6716'].mean.value)
#         min_std_kms = temp_std_kms - ((frac_temp/100)*temp_std_kms)
#         max_std_kms = temp_std_kms + ((frac_temp/100)*temp_std_kms)

#         min_std_ha = mfit.velspace_to_lamspace(min_std_kms, 6564.312)
#         max_std_ha = mfit.velspace_to_lamspace(max_std_kms, 6564.312)
        
#         g_ha_n = Gaussian1D(amplitude = amp_ha/2, mean = 6564.312, \
#                             stddev = temp_std, name = 'ha_n', \
#                             bounds = {'amplitude' : (0.0, None), 'stddev' : (0.85, None)})

#         ## Set narrow Ha within 60% of the template fit
#         g_ha_n.stddev.bounds = (min_std_ha, max_std_ha)
        
#         ## Outflow components
#         temp_out_std = sii_bestfit['sii6716_out'].stddev.value
#         temp_out_std_kms = mfit.lamspace_to_velspace(temp_out_std, \
#                                                      sii_bestfit['sii6716_out'].mean.value)

#         min_out_kms = temp_out_std_kms - ((frac_temp/100)*temp_out_std_kms)
#         max_out_kms = temp_out_std_kms + ((frac_temp/100)*temp_out_std_kms)

#         min_out = mfit.velspace_to_lamspace(min_out_kms, 6564.312)
#         max_out = mfit.velspace_to_lamspace(max_out_kms, 6564.312)

#         g_ha_out = Gaussian1D(amplitude = amp_ha/3, mean = 6564.312, \
#                              stddev = temp_out_std, name = 'ha_out', \
#                              bounds = {'amplitude': (0.0, None), 'stddev' : (0.85, None)})
        
#         g_ha_out.stddev.bounds = (min_out, max_out)
        
#         g_ha = g_ha_n + g_ha_out
        
#         ## Continuum
#         cont = Const1D(amplitude = 0.0, name = 'nii_ha_cont')
        
#         #####################################################################################
#         ########################## Fit without broad component ##############################

#         ## Initial gaussian fit
#         g_init = cont + g_nii + g_ha

#         fitter_no_broad = fitting.LevMarLSQFitter()

#         gfit_no_broad = fitter_no_broad(g_init, lam_nii, flam_nii,\
#                                      weights = np.sqrt(ivar_nii), maxiter = 1000)

        
#         rchi2_no_broad = mfit.calculate_red_chi2(flam_nii, gfit_no_broad(lam_nii),\
#                                                           ivar_nii, n_free_params = 11)

#         #####################################################################################
#         ########################## Fit with broad component #################################

#         ## Broad Ha parameters
#         g_ha_b = Gaussian1D(amplitude = amp_ha/2, mean = 6564.312, \
#                             stddev = 4.0, name = 'ha_b', \
#                             bounds = {'amplitude' : (0.0, None), 'stddev' : (1.5, None)})

#         ## Initial gaussian fit
#         g_init = cont + g_nii + g_ha + g_ha_b
#         fitter_broad = fitting.LevMarLSQFitter()

#         gfit_broad = fitter_broad(g_init, lam_nii, flam_nii,\
#                                   weights = np.sqrt(ivar_nii), maxiter = 1000)

        
#         rchi2_broad = mfit.calculate_red_chi2(flam_nii, gfit_broad(lam_nii), \
#                                                        ivar_nii, n_free_params = 14)
        
        
#         ## If broad-sigma < outflow-sigma -- exchange the gaussians
#         sigma_ha_b = mfit.lamspace_to_velspace(gfit_broad['ha_b'].stddev.value, \
#                                               gfit_broad['ha_b'].mean.value)
        
#         sigma_ha_out = mfit.lamspace_to_velspace(gfit_broad['ha_out'].stddev.value, \
#                                                 gfit_broad['ha_out'].mean.value)
        
#         if (sigma_ha_b < sigma_ha_out):
#             flag_bits = np.append(flag_bits, 6)
#             g_ha_n = Gaussian1D(amplitude = gfit_broad['ha_n'].amplitude, \
#                                mean = gfit_broad['ha_n'].mean, \
#                                stddev = gfit_broad['ha_n'].stddev, name = 'ha_n')
            
#             g_ha_out = Gaussian1D(amplitude = gfit_broad['ha_b'].amplitude, \
#                                  mean = gfit_broad['ha_b'].mean, \
#                                  stddev = gfit_broad['ha_b'].stddev, name = 'ha_out')
            
#             g_ha_b = Gaussian1D(amplitude = gfit_broad['ha_out'].amplitude, \
#                                mean = gfit_broad['ha_out'].mean, \
#                                 stddev = gfit_broad['ha_out'].stddev, name = 'ha_b')
            
#             gfit_broad = g_ha_n + g_ha_out + g_ha_b

#         #####################################################################################
#         #####################################################################################

#         ## Select the best-fit based on rchi2
#         ## If the rchi2 of 2-component is better by 20%, then the 2-component fit is picked.
#         ## Otherwise, 1-component fit is the best fit.
#         del_rchi2 = ((rchi2_no_broad - rchi2_broad)/rchi2_no_broad)*100
        
#         ## Also sigma (broad Ha) > sigma (narrow Ha)
#         sig_ha_b = mfit.lamspace_to_velspace(gfit_broad['ha_b'].stddev.value, \
#                                              gfit_broad['ha_b'].mean.value)
#         sig_ha_n = mfit.lamspace_to_velspace(gfit_broad['ha_n'].stddev.value, \
#                                              gfit_broad['ha_n'].mean.value)
        
#         fwhm_ha_b = 2.355*sig_ha_b
        
#         ## Set flags
#         flag_bits = np.append(flag_bits, 2)
#         if (del_rchi2 >= 20):
#             flag_bits = np.append(flag_bits, 4)
#         if (sig_ha_b < sig_ha_n):
#             flag_bits = np.append(flag_bits, 5)
#         if (sig_ha_n < 40):
#             flag_bits = np.append(flag_bits, 10)
            
#         flag_bits = np.sort(flag_bits.astype(int))

#         if ((del_rchi2 >= 20)&(sig_ha_b > sig_ha_n)&(sig_ha_n >= 40.)&(fwhm_ha_b >= 300.)):
#             return (gfit_broad, rchi2_broad, flag_bits, del_rchi2)
#         else:
#             return (gfit_no_broad, rchi2_no_broad, flag_bits, del_rchi2)

# ####################################################################################################
    
#     def fit_fixed_one_component(lam_nii, flam_nii, ivar_nii, sii_bestfit):
#         """
#         Function to fit [NII]6548, 6583 emission lines.
#         The code uses [SII] best fit as a template for both [NII] and Ha.
#         The broad component fit needs to be >20% better to be picked.
#         Code works only for single-component [SII] fits. No outflow components.
        
#         Parameters
#         ----------
#         lam_nii : numpy array
#             Wavelength array of the [NII]+Ha region where the fits need to be performed.
#         flam_nii : numpy array
#             Flux array of the spectra in the [NII]+Ha region.
#         ivar_nii : numpy array
#             Inverse variance array of the spectra in the [NII]+Ha region.
            
#         sii_bestfit : Astropy model
#             Best fit model for the [SII] emission-lines.
            
#         Returns
#         -------
#         gfit : Astropy model
#             Best-fit 1 component model
#         rchi2: float
#             Reduced chi2 of the best-fit
            
#         flag_bits : numpy array
#             Array of flag bits for free one-component fitting
#                 2 : free two component fit
#                 4 : chi^2 for broad-line fit improves by 20%
#                 5 : sigma (Ha; b) < sigma (Ha; n)
                
#         del_rchi2 : float
#             Percentage difference between rchi2 with and without broad-line.
#         """
        
#         flag_bits = np.array([])
        
#         ## Initial estimate of amplitudes
#         amp_nii6548 = np.max(flam_nii[(lam_nii > 6548)&(lam_nii < 6550)])
#         amp_nii6583 = np.max(flam_nii[(lam_nii > 6583)&(lam_nii < 6586)])
        
#         ## Initial guess of amplitude for Ha
#         amp_ha = np.max(flam_nii[(lam_nii > 6550)&(lam_nii < 6575)])
        
#         ## Initial estimates of standard deviation
#         stddev_nii6548 = (6549.852/sii_bestfit['sii6716'].mean.value)*\
#         sii_bestfit['sii6716'].stddev.value
#         stddev_nii6583 = (6585.277/sii_bestfit['sii6716'].mean.value)*\
#         sii_bestfit['sii6716'].stddev.value

#         ## Single component fits
#         g_nii6548 = Gaussian1D(amplitude = amp_nii6548, mean = 6549.852, \
#                                stddev = stddev_nii6548, name = 'nii6548', \
#                                bounds = {'amplitude' : (0.0, None)})
#         g_nii6583 = Gaussian1D(amplitude = amp_nii6583, mean = 6585.277, \
#                                stddev = stddev_nii6583, name = 'nii6583', \
#                                bounds = {'amplitude' : (0.0, None)})

#         ## Tie means of [NII] doublet gaussians
#         def tie_mean_nii(model):
#             return (model['nii6548'].mean + 35.425)

#         g_nii6583.mean.tied = tie_mean_nii

#         ## Tie amplitudes of two [NII] gaussians
#         def tie_amp_nii(model):
#             return (model['nii6548'].amplitude*2.96)

#         g_nii6583.amplitude.tied = tie_amp_nii

#         ## Tie standard deviations of all the narrow components
#         def tie_std_nii6548(model):
#             return ((model['nii6548'].mean/sii_bestfit['sii6716'].mean)*\
#                     sii_bestfit['sii6716'].stddev)

#         g_nii6548.stddev.tied = tie_std_nii6548
#         g_nii6548.stddev.fixed = True

#         def tie_std_nii6583(model):
#             return ((model['nii6583'].mean/sii_bestfit['sii6716'].mean)*\
#                     sii_bestfit['sii6716'].stddev)

#         g_nii6583.stddev.tied = tie_std_nii6583
#         g_nii6583.stddev.fixed = True

#         g_nii = g_nii6548 + g_nii6583

#         ## Ha parameters
#         ## Model narrow Ha as narrow [SII]
#         stddev_ha = (6564.312/sii_bestfit['sii6716'].mean.value)*\
#         sii_bestfit['sii6716'].stddev.value

#         g_ha_n = Gaussian1D(amplitude = amp_ha, mean = 6564.312, \
#                             stddev = stddev_ha, name = 'ha_n', \
#                             bounds = {'amplitude' : (0.0, None), 'stddev' : (0.85, None)})

#         ## Tie standard deviation of Ha
#         def tie_std_ha(model):
#             return ((model['ha_n'].mean/sii_bestfit['sii6716'].mean)*\
#                     sii_bestfit['sii6716'].stddev)

#         g_ha_n.stddev.tied = tie_std_ha
#         g_ha_n.stddev.fixed = True

#         g_ha = g_ha_n
        
#         ## Continuum
#         cont = Const1D(amplitude = 0.0, name = 'nii_ha_cont')
        
#         #####################################################################################
#         ########################## Fit without broad component ##############################

#         ## Initial gaussian fit
#         g_init = cont + g_nii + g_ha

#         fitter_no_broad = fitting.LevMarLSQFitter()

#         gfit_no_broad = fitter_no_broad(g_init, lam_nii, flam_nii,\
#                                      weights = np.sqrt(ivar_nii), maxiter = 1000)

        
#         rchi2_no_broad = mfit.calculate_red_chi2(flam_nii, gfit_no_broad(lam_nii),\
#                                                           ivar_nii, n_free_params = 5)
        

#         #####################################################################################
#         ########################## Fit with broad component #################################

#         ## Broad Ha parameters
#         g_ha_b = Gaussian1D(amplitude = amp_ha/4, mean = 6564.312, \
#                             stddev = 5.0, name = 'ha_b', \
#                             bounds = {'amplitude' : (0.0, None), 'stddev' : (1.5, None)})

#         ## Initial gaussian fit
#         g_init = cont + g_nii + g_ha + g_ha_b
#         fitter_broad = fitting.LevMarLSQFitter()

#         gfit_broad = fitter_broad(g_init, lam_nii, flam_nii,\
#                                   weights = np.sqrt(ivar_nii), maxiter = 1000)

        
#         rchi2_broad = mfit.calculate_red_chi2(flam_nii, gfit_broad(lam_nii), \
#                                                        ivar_nii, n_free_params = 8)

#         #####################################################################################
#         #####################################################################################

#         ## Select the best-fit based on rchi2
#         ## If the rchi2 of 2-component is better by 20%, then the 2-component fit is picked.
#         ## Otherwise, 1-component fit is the best fit.
#         del_rchi2 = ((rchi2_no_broad - rchi2_broad)/rchi2_no_broad)*100
        
#         ## Also sigma (broad Ha) > sigma (narrow Ha)
#         sig_ha_b = mfit.lamspace_to_velspace(gfit_broad['ha_b'].stddev.value, \
#                                              gfit_broad['ha_b'].mean.value)
#         sig_ha_n = mfit.lamspace_to_velspace(gfit_broad['ha_n'].stddev.value, \
#                                              gfit_broad['ha_n'].mean.value)
        
#         fwhm_ha_b = 2.355*sig_ha_b
        
#         ## Set flags
#         flag_bits = np.append(flag_bits, 1)
#         if (del_rchi2 >= 20):
#             flag_bits = np.append(flag_bits, 4)
#         if (sig_ha_b < sig_ha_n):
#             flag_bits = np.append(flag_bits, 5)
#         if (sig_ha_n < 40):
#             flag_bits = np.append(flag_bits, 10)
            
#         flag_bits = np.sort(flag_bits.astype(int))

#         if ((del_rchi2 >= 20)&(sig_ha_b > sig_ha_n)&(fwhm_ha_b >= 300.)):
#             return (gfit_broad, rchi2_broad, flag_bits, del_rchi2)
#         else:
#             return (gfit_no_broad, rchi2_no_broad, flag_bits, del_rchi2)
        
# ####################################################################################################

#     def fit_fixed_two_components(lam_nii, flam_nii, ivar_nii, sii_bestfit):
#         """
#         Function to fit [NII]6548, 6583 emission lines.
#         The code uses [SII] best fit as a template for both [NII] and Ha.
#         The broad component fit needs to be >20% better to be picked.
#         Code works only for two-component [SII] fits, including outflow components.
        
#         Parameters
#         ----------
#         lam_nii : numpy array
#             Wavelength array of the [NII]+Ha region where the fits need to be performed.
#         flam_nii : numpy array
#             Flux array of the spectra in the [NII]+Ha region.
#         ivar_nii : numpy array
#             Inverse variance array of the spectra in the [NII]+Ha region.
            
#         sii_bestfit : Astropy model
#             Best fit model for the [SII] emission-lines.
            
#          Returns
#         -------
#         gfit : Astropy model
#             Best-fit 1 component model
#         rchi2: float
#             Reduced chi2 of the best-fit
            
#         flag_bits : numpy array
#             Array of flag bits for fixed two-component fitting
#                 3 : fixed one component fit
#                 4 : chi^2 for broad-line fit improves by 20%
#                 5 : sigma (Ha; b) < sigma (Ha; n)
                
#         del_rchi2 : float
#             Percentage difference between rchi2 with and without broad-line.
#         """
        
#         flag_bits = np.array([])
        
#         ## Initial estimate of amplitudes
#         amp_nii6548 = np.max(flam_nii[(lam_nii > 6548)&(lam_nii < 6550)])
#         amp_nii6583 = np.max(flam_nii[(lam_nii > 6583)&(lam_nii < 6586)])
        
#         ## Initial guess of amplitude for Ha
#         amp_ha = np.max(flam_nii[(lam_nii > 6550)&(lam_nii < 6575)])
        
#         ## Initial estimates of standard deviation
#         stddev_nii6548 = (6549.852/sii_bestfit['sii6716'].mean.value)*\
#         sii_bestfit['sii6716'].stddev.value
#         stddev_nii6583 = (6585.277/sii_bestfit['sii6716'].mean.value)*\
#         sii_bestfit['sii6716'].stddev.value
        
#         stddev_nii6548_out = (6549.852/sii_bestfit['sii6716_out'].mean.value)*\
#         sii_bestfit['sii6716_out'].stddev.value
#         stddev_nii6583_out = (6585.277/sii_bestfit['sii6716_out'].mean.value)*\
#         sii_bestfit['sii6716_out'].stddev.value

#         ## Two component fits
#         g_nii6548 = Gaussian1D(amplitude = amp_nii6548/2, mean = 6549.852, \
#                                stddev = stddev_nii6548, name = 'nii6548', \
#                                bounds = {'amplitude' : (0.0, None)})
#         g_nii6583 = Gaussian1D(amplitude = amp_nii6583/2, mean = 6585.277, \
#                                stddev = stddev_nii6583, name = 'nii6583', \
#                                bounds = {'amplitude' : (0.0, None)})

#         g_nii6548_out = Gaussian1D(amplitude = amp_nii6548/4, mean = 6549.852, \
#                                    stddev = stddev_nii6548_out, name = 'nii6548_out', \
#                                    bounds = {'amplitude' : (0.0, None)})
#         g_nii6583_out = Gaussian1D(amplitude = amp_nii6583/4, mean = 6585.277, \
#                                    stddev = stddev_nii6583_out, name = 'nii6583_out', \
#                                    bounds = {'amplitude' : (0.0, None)})

#         ## Tie means of [NII] doublet gaussians
#         def tie_mean_nii(model):
#             return (model['nii6548'].mean + 35.425)

#         g_nii6583.mean.tied = tie_mean_nii

#         ## Tie amplitudes of two [NII] gaussians
#         def tie_amp_nii(model):
#             return (model['nii6548'].amplitude*2.96)

#         g_nii6583.amplitude.tied = tie_amp_nii

#         ## Tie standard deviations of all the narrow components
#         def tie_std_nii6548(model):
#             return ((model['nii6548'].mean/sii_bestfit['sii6716'].mean)*\
#                     sii_bestfit['sii6716'].stddev)

#         g_nii6548.stddev.tied = tie_std_nii6548
#         g_nii6548.stddev.fixed = True

#         def tie_std_nii6583(model):
#             return ((model['nii6583'].mean/sii_bestfit['sii6716'].mean)*\
#                     sii_bestfit['sii6716'].stddev)

#         g_nii6583.stddev.tied = tie_std_nii6583
#         g_nii6583.stddev.fixed = True

#         ## Tie means of [NII] outflow components
#         def tie_mean_nii_out(model):
#             return (model['nii6548_out'].mean + 35.425)

#         g_nii6583_out.mean.tied = tie_mean_nii_out

#         ## Tie amplitudes of two [NII] gaussians
#         def tie_amp_nii_out(model):
#             return (model['nii6548_out'].amplitude*2.96)

#         g_nii6583_out.amplitude.tied = tie_amp_nii_out

#         ## Tie standard deviations of all the outflow components
#         def tie_std_nii6548_out(model):
#             return ((model['nii6548_out'].mean/sii_bestfit['sii6716_out'].mean)*\
#                     sii_bestfit['sii6716_out'].stddev)

#         g_nii6548_out.stddev.tied = tie_std_nii6548_out
#         g_nii6548_out.stddev.fixed = True

#         def tie_std_nii6583_out(model):
#             return ((model['nii6583_out'].mean/sii_bestfit['sii6716_out'].mean)*\
#                     sii_bestfit['sii6716_out'].stddev)

#         g_nii6583_out.stddev.tied = tie_std_nii6583_out
#         g_nii6583_out.stddev.fixed = True

#         g_nii = g_nii6548 + g_nii6583 + g_nii6548_out + g_nii6583_out

#         ### Halpha Parameters ##

#         ## Ha parameters
#         ## Model narrow Ha as narrow [SII]
#         stddev_ha = (6564.312/sii_bestfit['sii6716'].mean.value)*\
#         sii_bestfit['sii6716'].stddev.value
#         ## Model outflow Ha as outflow [SII]
#         stddev_ha_out = (6564.312/sii_bestfit['sii6716_out'].mean.value)*\
#         sii_bestfit['sii6716_out'].stddev.value

#         g_ha_n = Gaussian1D(amplitude = amp_ha/2, mean = 6564.312, \
#                             stddev = stddev_ha, name = 'ha_n', \
#                             bounds = {'amplitude' : (0.0, None), 'stddev' : (0.85, None)})

#         g_ha_out = Gaussian1D(amplitude = amp_ha/3, mean = 6564.312, \
#                               stddev = stddev_ha_out, name = 'ha_out', \
#                               bounds = {'amplitude' : (0.0, None), 'stddev' : (0.85, None)})

#         ## Tie standard deviation of Ha
#         def tie_std_ha(model):
#             return ((model['ha_n'].mean/sii_bestfit['sii6716'].mean)*\
#                     sii_bestfit['sii6716'].stddev)

#         g_ha_n.stddev.tied = tie_std_ha
#         g_ha_n.stddev.fixed = True

#         ## Tie standard deviation of Ha outflow
#         def tie_std_ha_out(model):
#             return ((model['ha_out'].mean/sii_bestfit['sii6716_out'].mean)*\
#                     sii_bestfit['sii6716_out'].stddev)

#         g_ha_out.stddev.tied = tie_std_ha_out
#         g_ha_out.stddev.fixed = True

#         g_ha = g_ha_n + g_ha_out
        
#         ## Continuum
#         cont = Const1D(amplitude = 0.0, name = 'nii_ha_cont')
        
#         #####################################################################################
#         ########################## Fit without broad component ##############################

#         ## Initial gaussian fit
#         g_init = cont + g_nii + g_ha

#         fitter_no_broad = fitting.LevMarLSQFitter()

#         gfit_no_broad = fitter_no_broad(g_init, lam_nii, flam_nii,\
#                                      weights = np.sqrt(ivar_nii), maxiter = 1000)

        
#         rchi2_no_broad = mfit.calculate_red_chi2(flam_nii, gfit_no_broad(lam_nii),\
#                                                           ivar_nii, n_free_params = 9)

#         #####################################################################################
#         ########################## Fit with broad component #################################

#         ## Broad Ha parameters
#         g_ha_b = Gaussian1D(amplitude = amp_ha/2, mean = 6564.312, \
#                             stddev = 4.0, name = 'ha_b', \
#                             bounds = {'amplitude' : (0.0, None), 'stddev' : (1.5, None)})
        
        
#         ## Initial gaussian fit
#         g_init = cont + g_nii + g_ha + g_ha_b
#         fitter_broad = fitting.LevMarLSQFitter()

#         gfit_broad = fitter_broad(g_init, lam_nii, flam_nii,\
#                                   weights = np.sqrt(ivar_nii), maxiter = 1000)

        
#         rchi2_broad = mfit.calculate_red_chi2(flam_nii, gfit_broad(lam_nii), \
#                                                        ivar_nii, n_free_params = 12)

#         #####################################################################################
#         #####################################################################################

#         ## Select the best-fit based on rchi2
#         ## If the rchi2 of 2-component is better by 20%, then the 2-component fit is picked.
#         ## Otherwise, 1-component fit is the best fit.
#         del_rchi2 = ((rchi2_no_broad - rchi2_broad)/rchi2_no_broad)*100
        
#         ## Also sigma (broad Ha) > sigma (narrow Ha)
#         sig_ha_b = mfit.lamspace_to_velspace(gfit_broad['ha_b'].stddev.value, \
#                                              gfit_broad['ha_b'].mean.value)
#         sig_ha_n = mfit.lamspace_to_velspace(gfit_broad['ha_n'].stddev.value, \
#                                              gfit_broad['ha_n'].mean.value)
        
#         fwhm_ha_b = 2.355*sig_ha_b
        
#         ## Set flags
#         flag_bits = np.append(flag_bits, 3)
#         if (del_rchi2 >= 20):
#             flag_bits = np.append(flag_bits, 4)
#         if (sig_ha_b < sig_ha_n):
#             flag_bits = np.append(flag_bits, 5)
#         if (sig_ha_n < 40):
#             flag_bits = np.append(flag_bits, 10)
            
#         flag_bits = np.sort(flag_bits.astype(int))

#         if ((del_rchi2 >= 20)&(sig_ha_b > sig_ha_n)&(fwhm_ha_b >= 300.)):
#             return (gfit_broad, rchi2_broad, flag_bits, del_rchi2)
#         else:
#             return (gfit_no_broad, rchi2_no_broad, flag_bits, del_rchi2)
        
# ####################################################################################################
# ####################################################################################################
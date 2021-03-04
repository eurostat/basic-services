/**
 * 
 */
package eu.europa.ec.eurostat.basicservices.healthcare;

import eu.europa.ec.eurostat.basicservices.BasicServicePublication;

/**
 * Publication script for healthcare.
 * 
 * @author julien Gaffuri
 *
 */
public class Publication {

	static String destinationBasePath = "E:\\dissemination\\shared-data\\MS_data\\";
	//static String destinationBasePath = "E:/users/gaffuju/eclipse_workspace/basic-services/";
	//static String destinationBasePath = "E:/users/clemoki/workspace/basic-services/";

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		BasicServicePublication.publish("healthcare", HealthcareUtil.path, destinationBasePath, HealthcareUtil.ccs, HealthcareUtil.cols_, HealthcareUtil.ats);
	}

}

import pandas as pd
import glob
import os


class FeatureScore:
    def __init__(self, all_files_args, flag):
        """
        init function.
        Declare variables, process data.
        """
        # all variables
        self.object_dict = self.dev_dict = self.ffsc_score_dict = {}
        all_files = all_files_args
        self.frame = pd.DataFrame
        list_of_df = []
        self.average_ffor_list = []
        self.dis_hbk_list = []
        self.mean_ffsc = self.n_range = 0

        # read csv files and build a data frame
        list_of_df = self.build_data_frame(all_files, list_of_df)

        self.frame = pd.concat(list_of_df)

        # frame as matrix because its easier to access values like this
        self.frame_matrix = self.frame.as_matrix()

        # bunch of functions called in sequence to get mean ffsc score and Nrange
        self.calculate_variance()
        self.ffor_score()
        self.affor_score()
        self.deviation_vector()
        self.ffsc_score()
        if flag is True:
            self.mean_nrange()
        else:
            self.mean_ffsc = fs.mean_ffsc
            self.n_range = fs.n_range

        # just for now, we are calling dis_hbk_score for everything to understand.
        # TODO: move it back to else
        self.dis_hbk_score()

    @staticmethod
    def build_data_frame(all_files, list_of_df):
        for file_ in all_files:
            df = pd.read_csv(file_, index_col=None, header=0)
            list_of_df.append(df)
        return list_of_df

    def calculate_variance(self):
        """
        Function which calculates variance of IP addresses given a data frame.
        data frame has total and unique ip addresses.
        variance of IP addresses can be defined as changing rate of IP's in a specific time window.
        We consider window to be a day since we have data per day. And we calculate variance with the following formula:
        variance = unique_ip_addresses (per day) / total_#_of_ip_addresses (per day)
        :return: None
        we update data frame and data frame matrix for future use
        """
        variance_list = []
        for z in range(len(self.frame.index)):
            variance_list.append(self.frame_matrix[z][1] / self.frame_matrix[z][0])
        del self.frame['total_ip']
        del self.frame['unique_ip']
        var = pd.Series(variance_list)
        self.frame['variance'] = var.values
        self.frame_matrix = self.frame.as_matrix()

    def ffor_score(self):
        """
        Function which calculates ffor_score for all the objects.
        An object can have j features where 1 <= j <= n. Out of these j features, FFoR of feature i can be calculated:
        FFoR of object O for feature i = summation of |feature_i - feature_j|
        Here feature_i != feature_j
        :return: None
        We update object_dictionary for each object with FFOR_Score for each feature.
        """
        # for all the rows we have
        for z in range(len(self.frame.index)):
            # this will have FFOR value for each object's feature
            sum_list = []
            # for all the features
            for i in range(len(self.frame.columns)):
                # variable used for summation
                sum_val = 0
                # another loop because we want to check against all the other columns
                for j in range(len(self.frame.columns)):
                    # feature value shouldn't subtract against itself
                    if j != i:
                        # summation
                        sum_val = sum_val + abs(self.frame_matrix[z][i] -
                                                self.frame_matrix[z][j])
                # add summation value for each of the features
                sum_list.append(sum_val)
            # add this list to the object as value
            self.object_dict[z] = sum_list

    def affor_score(self):
        """
        Function which calculates AFFoR score which is mean of FFoR score.
        :return: None
        Updates average FFoR list with mean values which would be used to calculate deviation vector
        """
        for z in range(len(self.object_dict)):
            mean_of_values = sum(self.object_dict[z]) / len(self.frame.columns)
            self.average_ffor_list.append(mean_of_values)

    def deviation_vector(self):
        """
        Function which calculates deviation vector.
        Deviation vector is absolute difference between FFoR value and AFFoR value for all the features of an object
        :return: None
        update deviation_dictionary with deviation scores for each object
        """
        for z in range(len(self.frame.index)):
            dev_list = []
            for i in range(len(self.frame.columns)):
                dev = abs(self.frame_matrix[z][i] - self.average_ffor_list[z])
                dev_list.append(dev)
            self.dev_dict[z] = dev_list

    def ffsc_score(self):
        """
        Function which calculates FFSC score. FFSC is defined as degree of similarity between deviation and mean values.
        For an Object i, FFSC can be calculated as:
        numerator = feature vector for Object_i * transpose of deviation_vector for Object_i
        Numerator will be a (1 * 3) * (3 * 1) multiplication and result would be a single digit.
        denominator = mean(all features of Object_i) + mean(Deviation vector of Object_i)
        FFSC = numerator / denominator
        :return: None
        Update ffsc score dictionary with FFSC score for each object
        """
        dev_t = self.get_transpose()
        dev = self.dev_dict.values()
        for z in range(len(self.frame.index)):
            sum_val = 0
            for i in range(len(self.frame_matrix[z])):
                sum_val += self.frame_matrix[z][i] * dev_t[z][i]
            numerator = sum_val
            denominator = ((sum(self.frame_matrix[z] / float(len(self.frame_matrix[z]))))
                           + (sum(dev[z]) / float(len(dev[z]))))
            self.ffsc_score_dict[z] = numerator / denominator

    def mean_nrange(self):
        """
        Function which calculates mean and Nrange based on FFSC scores.
        mean is mean of all ffsc scores
        Nrange is maximum ffsc score - minimum ffsc score
        :return: None
        updates mean_ffsc and n_range
        """
        self.mean_ffsc = sum(self.ffsc_score_dict.values()) / len(self.ffsc_score_dict.values())
        maxx = max(self.ffsc_score_dict.values())
        minn = min(self.ffsc_score_dict.values())
        self.n_range = maxx - minn

    def get_transpose(self):
        """
        Helper function to calculate transpose of a deviation vector.
        :return: transposed deviation vector
        """
        dev_t = map(list, zip(*self.dev_dict.values()))
        dev_t_final = []
        for i in range(len(self.dev_dict.values())):
            dev_t_intermediate = [l[i] for l in dev_t]
            dev_t_final.append(dev_t_intermediate)
        return dev_t_final

    def dis_hbk_score(self):
        """
        Function which calculates dis_HBK score.
        :return:
        updates disk_hbk_list with dis_hbk_score values
        """
        for z in range(len(self.frame.index)):
            self.dis_hbk_list.append(abs(self.ffsc_score_dict.values()[z] - self.mean_ffsc) / self.n_range)

script_dir = os.path.dirname(__file__)
train_files = glob.glob(os.path.join(script_dir, 'csv_inside/train/*.csv'))
validation_files = glob.glob(os.path.join(script_dir, 'csv_inside/validate/*.csv'))
test_files = glob.glob(os.path.join(script_dir, 'csv_inside/test/*.csv'))
fs = FeatureScore(train_files, True)
vs = FeatureScore(validation_files, False)
ts = FeatureScore(test_files, False)
# print fs.frame
# print len(fs.frame.columns)
# print fs.object_dict
# print len(fs.object_dict)
# print fs.average_ffor_list
# print len(fs.average_ffor_list)
# print fs.dev_dict
# print len(fs.dev_dict)
# print fs.dev_dict.values()

# print map(list, zip(*fs.dev_dict.values()))
print "------------------TRAIN------------------"
print "FFSc Score "
print fs.ffsc_score_dict
print "MFFSc "
print fs.mean_ffsc
print "NRange "
print fs.n_range
print "dis_HBK "
print fs.dis_hbk_list
print fs.frame['variance']
print "----------------VALIDATION---------------"
print "FFSc Score"
print vs.ffsc_score_dict
print "MFFSc "
print vs.mean_ffsc
print "NRange "
print vs.n_range
print "dis_HBK "
print vs.dis_hbk_list
print "-------------------TEST------------------"
print "FFSc Score"
print ts.ffsc_score_dict
print "MFFSc "
print ts.mean_ffsc
print "NRange "
print ts.n_range
print "dis_HBK "
print ts.dis_hbk_list
